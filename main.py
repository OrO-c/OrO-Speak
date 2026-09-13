from src.pipesay.fetcher.fetcher import Fetcher
from src.pipesay.outputers import outputer_utils  # noqa: F401
from src.pipesay.outputers.base import Outputer
from src.pipesay.parser.parser import arg_process
from src.pipesay.processor import processer_utils  # noqa: F401
from src.pipesay.processor.base import Processor
from src.pipesay.utils.utils import clear_screen, enter_to_next


def main():
    args = arg_process()
    fetcher = Fetcher(args.get('fetcher_mode'), args.get('generations'), args.get('category'), args.get('file_path'),).new_fetcher()
    fetch_sentences = fetcher()
    processor = Processor(config_path=args.get('processer_config'))
    speak_sentences = processor.process(fetch_sentences)
    enter_to_next("已经处理完成，按回车开始输出")
    clear_screen()
    outputer = Outputer(config_path=args.get('outputer_config'))
    outputer.fire(speak_sentences)

if __name__ == "__main__":
    main()