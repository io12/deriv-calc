#!/usr/bin/env python3

import cmd

import expr


class DerivCalc(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = 'deriv-calc> '

    def do_quit(self, line):
        return True

    def do_exit(self, line):
        return True

    def do_EOF(self, line):
        print('exit')
        return True

    def do_simpl(self, line):
        print(expr.parse(line).simpl())

    def default(self, line):
        print(expr.parse(line).deriv().simpl())


if __name__ == '__main__':
    DerivCalc().cmdloop()
