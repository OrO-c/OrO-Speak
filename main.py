from fetcher.fetcher import Fetcher
from outputers import outputer_utils  # noqa: F401
from outputers.base import Outputer
from parser.parser import arg_process
from speakers import speak_utils  # noqa: F401
from speakers.base import Speaker
from utils.utils import clear_screen, enter_to_next


def main():
    args = arg_process()
    fetcher = Fetcher(args.get('fetcher_mode'), args.get('generations'), args.get('category'), args.get('file_path'),).new_fetcher()
    fetch_sentences = fetcher()
    speaker = Speaker(config_path=args.get('speaker_config'))
    speak_sentences = speaker.process(fetch_sentences)
    enter_to_next("已经处理完成，按回车开始输出")
    clear_screen()
    outputer = Outputer(config_path=args.get('outputer_config'))
    outputer.fire(speak_sentences)

if __name__ == "__main__":
    main()