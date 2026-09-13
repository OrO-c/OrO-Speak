import asyncio
import inspect
from collections.abc import Callable
from functools import wraps

import yaml

# 全局输出器注册表
OUTPUTER_REGISTRY: dict[str, dict] = {}


def outputer(name: str | None = None):
    """
    装饰器：注册输出器
    使用方式：
        @outputer('console')
        def console_output(text, color='green', log=None):
            print(f"\033[32m{text}\033[0m")
    """
    def decorator(func: Callable):
        outputer_name = name or func.__name__
        
        sig = inspect.signature(func)
        params = {}
        for param_name, param in sig.parameters.items():
            if param_name in ('self', 'sentences', 'log'):  # ← log 是内部参数，不暴露给配置
                continue
            if param.default != inspect.Parameter.empty:
                params[param_name] = {
                    'type': type(param.default).__name__,
                    'default': param.default,
                    'required': False
                }
            else:
                params[param_name] = {
                    'type': 'any',
                    'default': None,
                    'required': True
                }
        
        OUTPUTER_REGISTRY[outputer_name] = {
            'func': func,
            'params': params,
            'doc': func.__doc__ or ''
        }
        
        @wraps(func)
        def wrapper(text, **kwargs):
            log_cb = kwargs.pop('log', None)  # ← 从 kwargs 里取出 log
            return func(text, **kwargs, log=log_cb)  # ← 传给真正的函数
        return wrapper
    return decorator


class Outputer:
    """输出执行器（使用 log 代替 progress 回调）"""
    
    def __init__(self, config_path: str | None = None, config_dict: dict | None = None):
        if config_dict:
            self.config = config_dict
        elif config_path:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        else:
            raise ValueError("必须提供config_path或config_dict")
        
        self.outputs = self.config.get('outputs', [])
        self.global_config = self.config.get('global', {})
    
    def fire(self, sentences: list) -> None:
        """把文本依次发送给所有输出器"""
        def log(message: str):
            print(message)
        
        for step in self.outputs:
            outputer_name = step.get('outputer')
            params = step.get('params', {})
            
            if outputer_name not in OUTPUTER_REGISTRY:
                raise ValueError(f"未知输出器: {outputer_name}，已注册: {list(OUTPUTER_REGISTRY.keys())}")
            
            log(f'📤 开始输出到 {outputer_name}')
            
            final_params = {**self.global_config.get(outputer_name, {}), **params}
            final_params['log'] = log
            
            func = OUTPUTER_REGISTRY[outputer_name]['func']
            try:
                result = func(sentences, **final_params)
                # 如果返回的是协程，说明这是个异步输出器，需要驱动它
                if inspect.iscoroutine(result):
                    asyncio.run(result)
                log(f'✅ {outputer_name} 输出完成')
            except Exception as e:
                log(f'❌ {outputer_name} 失败: {e}')
                raise
    
    @staticmethod
    def list_outputers():
        """列出所有可用输出器"""
        print("\n" + "="*60)
        print("可用的输出器列表:")
        print("="*60)
        for name, info in OUTPUTER_REGISTRY.items():
            print(f"\n【{name}】")
            if info['doc']:
                print(f"  说明: {info['doc']}")
            if info['params']:
                print("  参数:")
                for pname, pinfo in info['params'].items():
                    required = "必填" if pinfo['required'] else "可选"
                    default = f"，默认: {pinfo['default']}" if pinfo['default'] is not None else ""
                    print(f"    - {pname}: {pinfo['type']} ({required}{default})")
            else:
                print("  无参数")
        print("="*60)