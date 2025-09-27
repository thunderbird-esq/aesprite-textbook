#!/usr/bin/env python3
"""
performance_optimization.py - Speed and resource optimization for the generation pipeline
"""

import time
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
from PIL import Image
import pickle
import json
import hashlib
import lru_cache
from collections import OrderedDict
import gc
import weakref
import asyncio
import aiofiles
import aiohttp
from queue import Queue, PriorityQueue
import multiprocessing as mp
from functools import wraps
import logging

@dataclass
class PerformanceMetrics:
    """Track performance metrics for optimization"""
    operation_name: str
    start_time: float
    end_time: float = 0
    memory_before: int = 0
    memory_after: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    items_processed: int = 0
    errors: int = 0
    
    @property
    def duration(self) -> float:
        """Calculate operation duration"""
        return self.end_time - self.start_time
    
    @property
    def memory_delta(self) -> int:
        """Calculate memory usage change"""
        return self.memory_after - self.memory_before
    
    @property
    def throughput(self) -> float:
        """Calculate items per second"""
        if self.duration > 0:
            return self.items_processed / self.duration
        return 0
    
    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.cache_hits + self.cache_misses
        if total > 0:
            return self.cache_hits / total
        return 0


class PerformanceMonitor:
    """Monitor and log performance metrics"""
    
    def __init__(self):
        self.metrics = {}
        self.logger = logging.getLogger(__name__)
        
    def start_operation(self, name: str) -> PerformanceMetrics:
        """Start monitoring an operation"""
        process = psutil.Process()
        memory = process.memory_info().rss
        
        metric = PerformanceMetrics(
            operation_name=name,
            start_time=time.time(),
            memory_before=memory
        )
        
        self.metrics[name] = metric
        return metric
    
    def end_operation(self, name: str):
        """End monitoring an operation"""
        if name in self.metrics:
            metric = self.metrics[name]
            metric.end_time = time.time()
            
            process = psutil.Process()
            metric.memory_after = process.memory_info().rss
            
            self.logger.info(f"Operation '{name}' completed:")
            self.logger.info(f"  Duration: {metric.duration:.2f}s")
            self.logger.info(f"  Memory delta: {metric.memory_delta / 1024 / 1024:.2f}MB")
            self.logger.info(f"  Throughput: {metric.throughput:.2f} items/s")
            self.logger.info(f"  Cache hit rate: {metric.cache_hit_rate:.2%}")
    
    def get_summary(self) -> Dict:
        """Get performance summary"""
        return {
            name: {
                'duration': metric.duration,
                'memory_delta_mb': metric.memory_delta / 1024 / 1024,
                'throughput': metric.throughput,
                'cache_hit_rate': metric.cache_hit_rate,
                'errors': metric.errors
            }
            for name, metric in self.metrics.items()
        }


def performance_timer(func: Callable) -> Callable:
    """Decorator to time function execution"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    
    return wrapper


def memory_profiler(func: Callable) -> Callable:
    """Decorator to profile memory usage"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        process = psutil.Process()
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        
        result = func(*args, **kwargs)
        
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        print(f"{func.__name__} memory delta: {mem_after - mem_before:.2f}MB")
        
        return result
    
    return wrapper


class OptimizedCache:
    """High-performance cache with size limits and LRU eviction"""
    
    def __init__(self, max_size_mb: int = 500, max_items: int = 1000):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.max_items = max_items
        self.cache = OrderedDict()
        self.size_tracker = {}
        self.current_size = 0
        self.hits = 0
        self.misses = 0
        self.lock = threading.Lock()
        
    def _estimate_size(self, obj: Any) -> int:
        """Estimate object size in bytes"""
        if isinstance(obj, Image.Image):
            # PIL Image size estimation
            return obj.width * obj.height * len(obj.getbands())
        elif isinstance(obj, np.ndarray):
            return obj.nbytes
        elif isinstance(obj, (str, bytes)):
            return len(obj)
        else:
            # Rough estimation for other objects
            return len(pickle.dumps(obj))
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        with self.lock:
            if key in self.cache:
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                self.hits += 1
                return self.cache[key]
            
            self.misses += 1
            return None
    
    def put(self, key: str, value: Any):
        """Put item in cache with LRU eviction"""
        with self.lock:
            # Estimate size
            size = self._estimate_size(value)
            
            # Remove existing if present
            if key in self.cache:
                self.current_size -= self.size_tracker[key]
                del self.cache[key]
                del self.size_tracker[key]
            
            # Evict items if necessary
            while (self.current_size + size > self.max_size_bytes or 
                   len(self.cache) >= self.max_items) and self.cache:
                
                oldest_key = next(iter(self.cache))
                self.current_size -= self.size_tracker[oldest_key]
                del self.cache[oldest_key]
                del self.size_tracker[oldest_key]
            
            # Add new item
            self.cache[key] = value
            self.size_tracker[key] = size
            self.current_size += size
    
    def clear(self):
        """Clear cache"""
        with self.lock:
            self.cache.clear()
            self.size_tracker.clear()
            self.current_size = 0
            self.hits = 0
            self.misses = 0
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        with self.lock:
            return {
                'items': len(self.cache),
                'size_mb': self.current_size / 1024 / 1024,
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': self.hits / max(self.hits + self.misses, 1)
            }


class ParallelProcessor:
    """Optimized parallel processing for different task types"""
    
    def __init__(self, max_workers: int = None):
        if max_workers is None:
            # Auto-detect optimal worker count
            cpu_count = mp.cpu_count()
            self.max_workers = min(cpu_count, 8)
        else:
            self.max_workers = max_workers
        
        self.logger = logging.getLogger(__name__)
        
    def process_io_bound(self, func: Callable, items: List[Any], 
                        desc: str = "Processing") -> List[Any]:
        """Process I/O-bound tasks using threads"""
        
        results = []
        errors = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_item = {
                executor.submit(func, item): item 
                for item in items
            }
            
            # Process results as they complete
            for future in as_completed(future_to_item):
                item = future_to_item[future]
                
                try:
                    result = future.result(timeout=30)
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Error processing {item}: {e}")
                    errors.append((item, str(e)))
        
        if errors:
            self.logger.warning(f"{len(errors)} errors during {desc}")
        
        return results
    
    def process_cpu_bound(self, func: Callable, items: List[Any],
                         desc: str = "Processing") -> List[Any]:
        """Process CPU-bound tasks using processes"""
        
        results = []
        
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Use map for better performance with processes
            results = list(executor.map(func, items))
        
        return results
    
    async def process_async(self, coro_func: Callable, items: List[Any],
                           max_concurrent: int = 10) -> List[Any]:
        """Process tasks asynchronously"""
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def bounded_coro(item):
            async with semaphore:
                return await coro_func(item)
        
        tasks = [bounded_coro(item) for item in items]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = []
        for result in results:
            if not isinstance(result, Exception):
                valid_results.append(result)
            else:
                self.logger.error(f"Async error: {result}")
        
        return valid_results


class ImageOptimizer:
    """Optimize image operations for performance"""
    
    def __init__(self):
        self.thumbnail_cache = OptimizedCache(max_size_mb=100)
        
    @performance_timer
    def batch_resize(self, images: List[Image.Image], 
                     target_size: Tuple[int, int]) -> List[Image.Image]:
        """Batch resize images efficiently"""
        
        def resize_single(img):
            # Use thumbnail for speed when downscaling
            if img.width > target_size[0] and img.height > target_size[1]:
                img.thumbnail(target_size, Image.Resampling.LANCZOS)
                return img
            else:
                return img.resize(target_size, Image.Resampling.LANCZOS)
        
        # Process in parallel
        processor = ParallelProcessor()
        return processor.process_io_bound(resize_single, images, "Resizing images")
    
    def create_thumbnail(self, image: Image.Image, size: int = 128) -> Image.Image:
        """Create cached thumbnail"""
        
        # Generate cache key
        img_hash = hashlib.md5(image.tobytes()).hexdigest()
        cache_key = f"thumb_{img_hash}_{size}"
        
        # Check cache
        cached = self.thumbnail_cache.get(cache_key)
        if cached:
            return cached
        
        # Create thumbnail
        thumb = image.copy()
        thumb.thumbnail((size, size), Image.Resampling.LANCZOS)
        
        # Cache it
        self.thumbnail_cache.put(cache_key, thumb)
        
        return thumb
    
    @staticmethod
    def optimize_save(image: Image.Image, path: str, format: str = 'PNG'):
        """Optimize image saving"""
        
        if format == 'PNG':
            # Optimize PNG compression
            image.save(path, 'PNG', optimize=True, compress_level=9)
        elif format == 'JPEG':
            # Optimize JPEG quality
            image.save(path, 'JPEG', quality=85, optimize=True)
        else:
            image.save(path, format)


class AssetPipeline:
    """Optimized asset generation pipeline"""
    
    def __init__(self):
        self.cache = OptimizedCache(max_size_mb=1000)
        self.processor = ParallelProcessor()
        self.image_optimizer = ImageOptimizer()
        self.monitor = PerformanceMonitor()
        self.queue = PriorityQueue()
        
    def generate_assets_optimized(self, configs: List[Dict]) -> Dict:
        """Generate assets with optimization"""
        
        metric = self.monitor.start_operation("asset_generation")
        
        # Sort by priority and estimated cost
        prioritized = self.prioritize_assets(configs)
        
        # Group by type for batch processing
        grouped = self.group_by_type(prioritized)
        
        results = {}
        
        for asset_type, group in grouped.items():
            # Check cache first
            cached, uncached = self.check_cache_batch(group)
            results.update(cached)
            
            # Generate uncached assets
            if uncached:
                if asset_type in ['graphic_photo_instructional', 'graphic_pixelart']:
                    # These are I/O bound (API calls)
                    new_assets = self.processor.process_io_bound(
                        self.generate_single_asset,
                        uncached,
                        f"Generating {asset_type}"
                    )
                else:
                    # CPU-bound generation
                    new_assets = self.processor.process_cpu_bound(
                        self.generate_single_asset,
                        uncached,
                        f"Generating {asset_type}"
                    )
                
                # Cache new assets
                for asset in new_assets:
                    if asset:
                        self.cache_asset(asset)
                        results[asset['id']] = asset
            
            metric.items_processed += len(group)
        
        self.monitor.end_operation("asset_generation")
        
        return results
    
    def prioritize_assets(self, configs: List[Dict]) -> List[Dict]:
        """Prioritize assets by importance and cost"""
        
        def calculate_priority(config):
            # Higher priority for critical elements
            priority_map = {
                'graphic_spiral_binding': 1,  # Always needed
                'graphic_photo_instructional': 2,  # Important
                'container_featurebox': 3,
                'graphic_pixelart': 4,
                'graphic_doodle': 5  # Least critical
            }
            
            base_priority = priority_map.get(config['type'], 10)
            
            # Adjust by size (larger = higher cost)
            size_factor = (config['dimensions'][0] * config['dimensions'][1]) / 1000000
            
            return base_priority + size_factor
        
        return sorted(configs, key=calculate_priority)
    
    def group_by_type(self, configs: List[Dict]) -> Dict[str, List[Dict]]:
        """Group configurations by type for batch processing"""
        
        grouped = {}
        for config in configs:
            asset_type = config['type']
            if asset_type not in grouped:
                grouped[asset_type] = []
            grouped[asset_type].append(config)
        
        return grouped
    
    def check_cache_batch(self, configs: List[Dict]) -> Tuple[Dict, List[Dict]]:
        """Check cache for multiple assets"""
        
        cached = {}
        uncached = []
        
        for config in configs:
            cache_key = self.get_cache_key(config)
            asset = self.cache.get(cache_key)
            
            if asset:
                cached[config['id']] = asset
                self.monitor.metrics.get('asset_generation', 
                                        PerformanceMetrics('', 0)).cache_hits += 1
            else:
                uncached.append(config)
                self.monitor.metrics.get('asset_generation', 
                                        PerformanceMetrics('', 0)).cache_misses += 1
        
        return cached, uncached
    
    def get_cache_key(self, config: Dict) -> str:
        """Generate cache key for configuration"""
        
        # Create deterministic key from config
        key_data = {
            'type': config['type'],
            'dimensions': config['dimensions'],
            'content': config.get('subject', config.get('text', ''))
        }
        
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    def cache_asset(self, asset: Dict):
        """Cache generated asset"""
        
        if asset and 'id' in asset:
            config = asset.get('config', {})
            cache_key = self.get_cache_key(config)
            self.cache.put(cache_key, asset)
    
    def generate_single_asset(self, config: Dict) -> Optional[Dict]:
        """Generate a single asset (simplified for example)"""
        
        try:
            # Simulate asset generation
            # In real implementation, this would call actual generation code
            
            if config['type'] == 'graphic_photo_instructional':
                # Simulate photo generation
                img = Image.new('RGB', tuple(config['dimensions']), (200, 180, 150))
            elif config['type'] == 'graphic_pixelart':
                # Simulate pixel art
                img = Image.new('RGB', (32, 32), (255, 0, 0))
                img = img.resize(tuple(config['dimensions']), Image.Resampling.NEAREST)
            else:
                # Generic colored box
                img = Image.new('RGB', tuple(config['dimensions']), (128, 128, 128))
            
            return {
                'id': config['id'],
                'image': img,
                'config': config
            }
        
        except Exception as e:
            logging.error(f"Failed to generate {config['id']}: {e}")
            return None


class MemoryManager:
    """Manage memory usage and cleanup"""
    
    def __init__(self, max_memory_mb: int = 2048):
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.weak_refs = weakref.WeakValueDictionary()
        self.logger = logging.getLogger(__name__)
        
    def check_memory(self) -> Dict:
        """Check current memory usage"""
        
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024,
            'percent': process.memory_percent(),
            'available_mb': psutil.virtual_memory().available / 1024 / 1024
        }
    
    def cleanup_if_needed(self, threshold: float = 0.8):
        """Trigger cleanup if memory usage exceeds threshold"""
        
        memory = self.check_memory()
        usage_ratio = memory['rss_mb'] * 1024 * 1024 / self.max_memory_bytes
        
        if usage_ratio > threshold:
            self.logger.warning(f"Memory usage at {usage_ratio:.1%}, triggering cleanup")
            self.force_cleanup()
    
    def force_cleanup(self):
        """Force garbage collection and clear caches"""
        
        # Clear image cache
        Image.core.clear_cache()
        
        # Force garbage collection
        gc.collect()
        
        # Clear weak references
        self.weak_refs.clear()
        
        self.logger.info("Memory cleanup completed")
    
    def track_object(self, key: str, obj: Any):
        """Track object with weak reference"""
        
        self.weak_refs[key] = obj
    
    def get_tracked_objects(self) -> Dict:
        """Get currently tracked objects"""
        
        return dict(self.weak_refs)


class OptimizationOrchestrator:
    """Orchestrate all optimization strategies"""
    
    def __init__(self):
        self.pipeline = AssetPipeline()
        self.memory_manager = MemoryManager()
        self.monitor = PerformanceMonitor()
        self.logger = logging.getLogger(__name__)
        
    async def generate_workbook_optimized(self, workbook_config: Dict) -> Dict:
        """Generate complete workbook with all optimizations"""
        
        overall_metric = self.monitor.start_operation("complete_workbook")
        
        results = {
            'spreads': [],
            'assets': {},
            'performance': {}
        }
        
        try:
            # Extract all asset configs
            all_configs = self.extract_asset_configs(workbook_config)
            
            # Generate assets in optimized pipeline
            self.logger.info(f"Generating {len(all_configs)} assets...")
            assets = self.pipeline.generate_assets_optimized(all_configs)
            results['assets'] = assets
            
            # Check memory after asset generation
            self.memory_manager.cleanup_if_needed()
            
            # Compose spreads in parallel
            spread_configs = workbook_config.get('spreads', [])
            
            self.logger.info(f"Composing {len(spread_configs)} spreads...")
            spreads = await self.compose_spreads_async(spread_configs, assets)
            results['spreads'] = spreads
            
            # Final memory cleanup
            self.memory_manager.force_cleanup()
            
        except Exception as e:
            self.logger.error(f"Workbook generation failed: {e}")
            overall_metric.errors += 1
            raise
        
        finally:
            self.monitor.end_operation("complete_workbook")
            results['performance'] = self.monitor.get_summary()
        
        return results
    
    def extract_asset_configs(self, workbook_config: Dict) -> List[Dict]:
        """Extract all asset configurations from workbook"""
        
        configs = []
        
        for spread in workbook_config.get('spreads', []):
            for page in ['left_page', 'right_page']:
                if page in spread:
                    for element in spread[page].get('elements', []):
                        configs.append(element)
        
        return configs
    
    async def compose_spreads_async(self, spread_configs: List[Dict], 
                                   assets: Dict) -> List[Dict]:
        """Compose spreads asynchronously"""
        
        async def compose_single(spread_config):
            # Simulate async composition
            # In real implementation, this would be actual composition
            await asyncio.sleep(0.1)
            
            return {
                'id': spread_config.get('id', 'unknown'),
                'status': 'complete'
            }
        
        processor = ParallelProcessor()
        return await processor.process_async(compose_single, spread_configs)
    
    def get_optimization_report(self) -> Dict:
        """Generate optimization report"""
        
        return {
            'cache_stats': self.pipeline.cache.get_stats(),
            'memory_usage': self.memory_manager.check_memory(),
            'performance_summary': self.monitor.get_summary()
        }


# Utility functions for optimization

def lazy_load_image(path: str) -> Image.Image:
    """Lazy load image only when needed"""
    
    class LazyImage:
        def __init__(self, path):
            self.path = path
            self._image = None
        
        def __getattr__(self, name):
            if self._image is None:
                self._image = Image.open(self.path)
            return getattr(self._image, name)
    
    return LazyImage(path)


def batch_operation(operation: Callable, items: List[Any], 
                   batch_size: int = 100) -> List[Any]:
    """Process items in batches for memory efficiency"""
    
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = [operation(item) for item in batch]
        results.extend(batch_results)
        
        # Allow garbage collection between batches
        gc.collect()
    
    return results


# Usage example
if __name__ == "__main__":
    import asyncio
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test optimization
    orchestrator = OptimizationOrchestrator()
    
    # Sample workbook configuration
    test_config = {
        'spreads': [
            {
                'id': 'spread_01_02',
                'left_page': {
                    'elements': [
                        {
                            'id': 'L_photo_01',
                            'type': 'graphic_photo_instructional',
                            'dimensions': [600, 450]
                        },
                        {
                            'id': 'L_container_01',
                            'type': 'container_featurebox',
                            'dimensions': [400, 200]
                        }
                    ]
                },
                'right_page': {
                    'elements': [
                        {
                            'id': 'R_pixel_01',
                            'type': 'graphic_pixelart',
                            'dimensions': [256, 256]
                        }
                    ]
                }
            }
        ]
    }
    
    # Run optimized generation
    async def run_test():
        results = await orchestrator.generate_workbook_optimized(test_config)
        
        print("\n=== Generation Complete ===")
        print(f"Assets generated: {len(results['assets'])}")
        print(f"Spreads composed: {len(results['spreads'])}")
        
        print("\n=== Performance Report ===")
        for op, metrics in results['performance'].items():
            print(f"{op}:")
            print(f"  Duration: {metrics['duration']:.2f}s")
            print(f"  Memory delta: {metrics['memory_delta_mb']:.2f}MB")
            print(f"  Cache hit rate: {metrics['cache_hit_rate']:.2%}")
        
        print("\n=== Optimization Report ===")
        report = orchestrator.get_optimization_report()
        print(f"Cache: {report['cache_stats']['items']} items, "
              f"{report['cache_stats']['size_mb']:.2f}MB, "
              f"{report['cache_stats']['hit_rate']:.2%} hit rate")
        print(f"Memory: {report['memory_usage']['rss_mb']:.2f}MB RSS, "
              f"{report['memory_usage']['percent']:.1f}% used")
    
    # Run the test
    asyncio.run(run_test())
