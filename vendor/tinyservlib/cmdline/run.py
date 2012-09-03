import argparse

def make_run(globs):
    def run():
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()

        for name in globs:
            if name.startswith('cmd_') and not name.endswith('_args'):
                cmdfunc = globs[name]
                cmdname = name[4:].replace('__', ':').replace('_', '-')
                subparser = subparsers.add_parser(cmdname,
                                                  help=cmdfunc.__doc__)
                subparser.set_defaults(func=cmdfunc)
                add_args = globs.get('%s_args' % name)
                if add_args:
                    add_args(subparser)
    
        args = parser.parse_args()
        args.func(args)

    return run
