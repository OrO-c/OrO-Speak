import asyncio

from desktop_notifier import DesktopNotifier, Urgency

from src.pipesay.outputers.base import outputer
from src.pipesay.utils.utils import clear_screen, enter_to_next


@outputer('term')
def normal_terminal(sentences: list, auto_clear: bool=True, log=None):
    for index, text in enumerate(sentences):
        print(text)
        if index + 1 != len(sentences):
            print("=" * 30)
            enter_to_next("按回车来看下一句吧！")
            print("\n\n")
            if auto_clear:
                clear_screen()


@outputer('file')
def to_file(sentences: list, file_path: str, log=None):
    lines = [item + '\n\n' for item in sentences]
    with open(file=file_path, mode='a', encoding='utf-8') as f:
        f.writelines(lines)

@outputer('notify')
async def notify(sentences: list, level: str='normal', log=None):
    URGENCY_MAP = {
        "low": Urgency.Low,
        "normal": Urgency.Normal,
        "critical": Urgency.Critical,
    }

    urgency = URGENCY_MAP[level]

    notifier = DesktopNotifier(app_name="批量通知演示")

    for message in sentences:
        await notifier.send(
            title="OrOspeak",
            message=message,
            urgency=urgency,
            sound=True,
        )

    await asyncio.sleep(3)

    log(f"已发送 {len(sentences)} 条通知，类型：{level}")