from .__init__ import app

@app.command()
def about() -> None:
    print('\n'.join([
        '-------------------------------------------------',
        '| bkdnOJ.v2 - Bach Khoa Da Nang Online Judge v2 |',
        '-------------------------------------------------',
        '',
        'This is a CLI for devs to quickly navigate and calling scripts.',
        '',
    ]))