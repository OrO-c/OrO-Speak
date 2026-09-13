from functools import wraps

import yaml

# ============================================================
# 1. 全局注册表（装饰器会自动填，你不用管）
# ============================================================
SPEAKER_REGISTRY = {}


# ============================================================
# 2. 装饰器：把函数注册到 SPEAKER_REGISTRY 里
# ============================================================
def speaker(name):
    """用这个装饰器注册工具，比如 @speaker('translate')"""
    def decorator(func):
        # 把函数存进注册表
        SPEAKER_REGISTRY[name] = {
            'func': func,
            'doc': func.__doc__ or ''
        }
        
        @wraps(func)
        def wrapper(text, **kwargs):
            return func(text, **kwargs)
        return wrapper
    return decorator


# ============================================================
# 3. Speaker 类：管道执行器
# ============================================================
class Speaker:
    def __init__(self, config_path=None, config_dict=None):
        """
        初始化 Speaker
        :param config_path: YAML 配置文件路径
        :param config_dict: 直接传配置字典（优先级高于 config_path）
        """
        # 加载配置
        if config_dict:
            self.config = config_dict
        elif config_path:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        else:
            raise ValueError("必须提供 config_path 或 config_dict")
        
        # 读取 pipeline 和全局配置
        self.pipeline = self.config.get('pipeline', [])
        self.global_config = self.config.get('global', {})
        
        # 定义日志函数（工具函数会调用它）
        def log(message):
            print(message)
        
        self.log = log
    
    def process(self, sentences):
        """
        执行管道处理
        :param sentences: 句子列表，比如 ["今天下雨了", "记得带伞"]
        :return: 处理后的结果列表
        """
        # 遍历管道里的每个工具
        current_texts = sentences
        for step_idx, step in enumerate(self.pipeline, 1):
            speaker_name = step.get('speaker')
            params = step.get('params', {})
            
            self.log(f'  ⏳ [{step_idx}/{len(self.pipeline)}] 执行 {speaker_name}')
            
            # 检查工具是否存在
            if speaker_name not in SPEAKER_REGISTRY:
                raise ValueError(f"未知工具: {speaker_name}")
            
            # 获取工具函数
            func = SPEAKER_REGISTRY[speaker_name]['func']
            
            # 合并参数（全局配置 + 局部配置）
            final_params = {**self.global_config.get(speaker_name, {}), **params}
            final_params['log'] = self.log   # 把日志函数塞进去
            
            # 执行工具
            try:
                current_texts = func(current_texts, **final_params)
                self.log(f'  ✅ {speaker_name} 完成')
            except Exception as e:
                self.log(f'  ❌ {speaker_name} 失败: {e}')
                raise
        self.log("Speaker全部处理完成！")
        
        return current_texts
    
    @staticmethod
    def list_speakers():
        """列出所有已注册的工具"""
        print("\n" + "=" * 50)
        print("已注册的工具:")
        for name, info in SPEAKER_REGISTRY.items():
            doc = info['doc']
            print(f"  - {name}: {doc}" if doc else f"  - {name}")
        print("=" * 50)