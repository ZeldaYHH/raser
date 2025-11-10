import math
import logging

logger = logging.getLogger(__name__)

max_size = 50000  # 50 mm
resolution_default ={'x': 1, 'y': 1, 'z': 1} 

class FieldCache:
    def __init__(self, my_f, resolution=resolution_default, fallback_field=None, bounds=None):  # 增加分辨率适应大型器件
        self.my_f = my_f
        try:
            self.resolution = resolution
            # 验证字典中的所有分辨率值
            for key, value in self.resolution.items():
                try:
                    float_value = float(value)
                    if float_value <= 0:
                        self.resolution[key] = resolution_default
                    else:
                        self.resolution[key] = float_value
                except (TypeError, ValueError):
                    self.resolution[key] = resolution_default
        except (TypeError, AttributeError):
            # 如果resolution不是字典，使用默认值
            logger.warning("Invalid resolution format, using default resolution: {}".format(resolution_default))
            self.resolution = resolution_default
        self.e_field_cache = {}
        self.doping_cache = {}
        self.w_p_cache = {}
        self.trap_h_cache = {}  # 空穴陷阱率缓存
        self.trap_e_cache = {}  # 电子陷阱率缓存
        self.fallback_field = list(fallback_field) if fallback_field is not None else None
        self.bounds = bounds or {}
        self._cache_stats = {
            'hits': 0, 'misses': 0, 'errors': 0, 'fallbacks': 0,
            'trap_h_hits': 0, 'trap_h_misses': 0,
            'trap_e_hits': 0, 'trap_e_misses': 0
        }
        logger.info(f"field cache initialization complete, resolution: {self.resolution} um")

    def get_e_field_cached(self, x, y, z):
        try:
            if not self._is_position_valid(x, y, z):
                return self._get_e_field(x, y, z)
                
            key_x, key_y, key_z = self._get_index_coords(x, y, z)
            key = (key_x, key_y, key_z)
            
            if key in self.e_field_cache:
                self._cache_stats['hits'] += 1
                return self.e_field_cache[key]
            else:
                self._cache_stats['misses'] += 1
                e_field = self._get_e_field(x, y, z)
                if e_field is not None:
                    self.e_field_cache[key] = e_field
                return e_field
                
        except Exception as e:
            self._cache_stats['errors'] += 1
            logger.warning(f"failed when getting field cache ({x:.1f}, {y:.1f}, {z:.1f}): {e}")
            return self._get_e_field(x, y, z)
    
    def get_doping_cached(self, x, y, z):
        try:
            if not self._is_position_valid(x, y, z):
                return self._get_doping(x, y, z)
                
            key_x, key_y, key_z = self._get_index_coords(x, y, z)
            key = (key_x, key_y, key_z)
            
            if key in self.doping_cache:
                return self.doping_cache[key]
            else:
                doping = self._get_doping(x, y, z)
                if doping is not None:
                    self.doping_cache[key] = doping
                return doping
        except Exception as e:
            logger.warning(f"failed when getting doping cache ({x:.1f}, {y:.1f}, {z:.1f}): {e}")
            return 0.0  # 默认掺杂浓度
        
    def get_w_p_cached(self, x, y, z, n):
        try:
            if not self._is_position_valid(x, y, z):
                return self._get_w_p(x, y, z, n)
            key_x, key_y, key_z = self._get_index_coords(x, y, z)
            key = (key_x, key_y, key_z, n)
            if key in self.w_p_cache:
                return self.w_p_cache[key]
            else:
                w_p = self._get_w_p(x, y, z, n)
                if w_p is not None:
                    self.w_p_cache[key] = w_p
                return w_p
        except Exception as e:
            logger.warning(f"failed when getting w_p cache ({x:.1f}, {y:.1f}, {z:.1f}, {n}): {e}")
            return 0.0  # 默认权重电势值
    
    def get_trap_h_cached(self, x, y, z):
        """获取空穴陷阱率 - 带缓存"""
        try:
            if not self._is_position_valid(x, y, z):
                return self._get_trap_h(x, y, z)
                
            key_x, key_y, key_z = self._get_index_coords(x, y, z)
            key = (key_x, key_y, key_z)
            
            if key in self.trap_h_cache:
                self._cache_stats['trap_h_hits'] += 1
                return self.trap_h_cache[key]
            else:
                self._cache_stats['trap_h_misses'] += 1
                trap_rate = self._get_trap_h(x, y, z)
                if trap_rate is not None:
                    self.trap_h_cache[key] = trap_rate
                return trap_rate
                
        except Exception as e:
            logger.warning(f"failed when getting hole trap rate cache ({x:.1f}, {y:.1f}, {z:.1f}): {e}")
            return 0.0  # 默认陷阱率
    
    def get_trap_e_cached(self, x, y, z):
        """获取电子陷阱率 - 带缓存"""
        try:
            if not self._is_position_valid(x, y, z):
                return self._get_trap_e(x, y, z)
                
            key_x, key_y, key_z = self._get_index_coords(x, y, z)
            key = (key_x, key_y, key_z)
            
            if key in self.trap_e_cache:
                self._cache_stats['trap_e_hits'] += 1
                return self.trap_e_cache[key]
            else:
                self._cache_stats['trap_e_misses'] += 1
                trap_rate = self._get_trap_e(x, y, z)
                if trap_rate is not None:
                    self.trap_e_cache[key] = trap_rate
                return trap_rate
                
        except Exception as e:
            logger.warning(f"failed when getting electron trap rate cache ({x:.1f}, {y:.1f}, {z:.1f}): {e}")
            return 0.0  # 默认陷阱率
    
    def _is_position_valid(self, x, y, z):
        if (abs(x) > max_size or abs(y) > max_size or abs(z) > max_size or
            math.isnan(x) or math.isnan(y) or math.isnan(z) or
            math.isinf(x) or math.isinf(y) or math.isinf(z)):
            return False
        return True
    
    def _get_index_coords(self, x, y, z):
        return (
            self._get_index_axis(x, 'x'),
            self._get_index_axis(y, 'y'),
            self._get_index_axis(z, 'z')
        )
    
    def _get_index_axis(self, value, axis):
        bounds = self.bounds.get(axis)
        idx = int(math.floor(value / self.resolution[axis]))
        if bounds:
            lower, upper = bounds
            if lower is not None:
                lower_idx = int(math.floor(lower / self.resolution[axis]))
                idx = max(idx, lower_idx)
            if upper is not None:
                # 略微缩小上边界，避免刚好落在网格外
                adjusted_upper = upper - 1e-6
                upper_idx = int(math.floor(adjusted_upper / self.resolution[axis]))
                idx = min(idx, upper_idx)
        return idx
    
    def _get_e_field(self, x, y, z):
        try:
            return self.my_f.get_e_field(x, y, z)
        except Exception as e:
            logger.warning(f"failed when getting e_field ({x:.1f}, {y:.1f}, {z:.1f}): {e}")
            if self.fallback_field is not None:
                self._cache_stats['fallbacks'] += 1
                return self.fallback_field
            return None
    
    def _get_doping(self, x, y, z):
        """安全的掺杂浓度获取"""
        try:
            return self.my_f.get_doping(x, y, z)
        except Exception as e:
            logger.warning(f"failed when getting doping ({x:.1f}, {y:.1f}, {z:.1f}): {e}")
            return 0.0
        
    def _get_w_p(self, x, y, z, n):
        """安全的权重电势获取"""
        try:
            return self.my_f.get_w_p(x, y, z, n)
        except Exception as e:
            logger.warning(f"failed when getting w_p ({x:.1f}, {y:.1f}, {z:.1f}, {n}): {e}")
            return 0.0
    
    def _get_trap_h(self, x, y, z):
        """安全的空穴陷阱率获取"""
        try:
            # 检查my_f是否有get_trap_h方法
            if hasattr(self.my_f, 'get_trap_h'):
                return self.my_f.get_trap_h(x, y, z)
            else:
                # 如果没有陷阱率方法，返回默认值0
                return 0.0
        except Exception as e:
            logger.warning(f"failed when getting hole trap rate ({x:.1f}, {y:.1f}, {z:.1f}): {e}")
            return 0.0
    
    def _get_trap_e(self, x, y, z):
        """安全的电子陷阱率获取"""
        try:
            # 检查my_f是否有get_trap_e方法
            if hasattr(self.my_f, 'get_trap_e'):
                return self.my_f.get_trap_e(x, y, z)
            else:
                # 如果没有陷阱率方法，返回默认值0
                return 0.0
        except Exception as e:
            logger.warning(f"failed when getting electron trap rate ({x:.1f}, {y:.1f}, {z:.1f}): {e}")
            return 0.0
    
    def get_cache_stats(self):
        total = self._cache_stats['hits'] + self._cache_stats['misses'] + self._cache_stats['errors']
        hit_rate = self._cache_stats['hits'] / total if total > 0 else 0
        
        # 陷阱率缓存统计
        trap_h_total = self._cache_stats['trap_h_hits'] + self._cache_stats['trap_h_misses']
        trap_h_hit_rate = self._cache_stats['trap_h_hits'] / trap_h_total if trap_h_total > 0 else 0
        
        trap_e_total = self._cache_stats['trap_e_hits'] + self._cache_stats['trap_e_misses']
        trap_e_hit_rate = self._cache_stats['trap_e_hits'] / trap_e_total if trap_e_total > 0 else 0
        
        return {
            'hits': self._cache_stats['hits'],
            'misses': self._cache_stats['misses'],
            'errors': self._cache_stats['errors'],
            'fallbacks': self._cache_stats['fallbacks'],
            'hit_rate': hit_rate,
            'total_entries': len(self.e_field_cache),
            'trap_h_hits': self._cache_stats['trap_h_hits'],
            'trap_h_misses': self._cache_stats['trap_h_misses'],
            'trap_h_hit_rate': trap_h_hit_rate,
            'trap_h_entries': len(self.trap_h_cache),
            'trap_e_hits': self._cache_stats['trap_e_hits'],
            'trap_e_misses': self._cache_stats['trap_e_misses'],
            'trap_e_hit_rate': trap_e_hit_rate,
            'trap_e_entries': len(self.trap_e_cache)
        }
    
    def clear_cache(self):
        """清空所有缓存"""
        self.e_field_cache.clear()
        self.doping_cache.clear()
        self.w_p_cache.clear()
        self.trap_h_cache.clear()
        self.trap_e_cache.clear()
        logger.info("所有缓存已清空")