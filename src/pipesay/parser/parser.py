import argparse

from pipesay.constants import constants


def _arg_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='PipeSay句子流水线')
    parser.add_argument('-g', '--generations', type=int, default=1, help='生成次数（默认：1）')
    parser.add_argument('-s', '--processor-config', dest="processer_config", type=str, default=None, help='processer流水线配置')
    parser.add_argument('-o', '--outputer-config', dest="outputer_config", type=str, default=None, help='outputer流水线配置')
    
    subparsers = parser.add_subparsers(dest='mode', required=True, help='选择获取模式')
    
    local_parser = subparsers.add_parser('local', help='从本地文件读取一言')
    local_parser.add_argument('-f', '--file', default=constants.DEFAULT_FILE, help='本地文件')
    
    hitokoto_parser = subparsers.add_parser('hitokoto', help='从网络获取')
    hitokoto_parser.add_argument('-c', '--category', nargs='*', choices=constants.YIYAN_CATEGORY.values(), default=constants.YIYAN_CATEGORY.values(), help='分类')

    return parser.parse_args()


def arg_process():
    args = _arg_parser()
    if args.generations <= 0:
        raise ValueError("请输入一个正整数生成次数")
    if args.mode == "local":
        if args.file == constants.DEFAULT_FILE:
            with open(args.file, 'a+', encoding="utf-8") as f:
                first_char = f.read(1)
                if not first_char:
                    print("语录文件是空的，已为您创建并写入了一定的内置语句")
                    with open(args.file, 'w', encoding="utf-8") as fw:
                        fw.writelines(constants.DEFAULT_LINES)
        else:
            try:
                with open(args.file, 'r', encoding="utf-8") as f:
                    first_char = f.read(1)
                    if not first_char:
                            raise RuntimeError(f"{args.file}是空的！")
            except FileNotFoundError:
                print("没有找到您的文件")
                raise
    
    config = {
        "fetcher_mode": args.mode,
        "generations": args.generations,
        "file_path": args.file if args.mode == 'local' else None,
        "category": args.category if args.mode == 'hitokoto' else None,
        "processer_config": args.processer_config,
        "outputer_config": args.outputer_config
    }
    return config