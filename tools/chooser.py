#!/usr/bin/env python

import curses

# based on https://github.com/coderholic/pyradio
# The MIT License
# Copyright (c) 2011 Ben Dowling
#
# FIXME(ja): add fuzzy search?

class Chooser(object):
    startPos = 0
    selection = 0

    def __init__(self, prompt, data):
        self.prompt = prompt
        self.data = data
        self.stdscr = None
        self.match = ''
        self.filtered = data

    def setup(self, stdscr):
        self.stdscr = stdscr

        try:
            curses.curs_set(0)
        except:
            pass

        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLUE)
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
        curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_BLUE)
        curses.init_pair(8, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_BLUE)

        self.stdscr.nodelay(0)
        self.setupAndDrawScreen()

        result = self.run()
        if result != -1:
            return result

    def setupAndDrawScreen(self):
        self.maxY, self.maxX = self.stdscr.getmaxyx()

        self.headWin = curses.newwin(1, self.maxX, 0, 0)
        self.bodyWin = curses.newwin(self.maxY - 1, self.maxX, 1, 0)
        self.initHead()
        self.initBody()

        self.bodyWin.keypad(1)

        curses.doupdate()

    def initHead(self):
        self.headWin.addstr(0, 0, self.prompt + ' ' + self.match)
        rightStr = "intern"
        self.headWin.addstr(0, self.maxX - len(rightStr) - 1, rightStr)
        self.headWin.bkgd(' ', curses.color_pair(0))
        self.headWin.noutrefresh()

    def initBody(self):
        self.bodyMaxY, self.bodyMaxX = self.bodyWin.getmaxyx()
        self.bodyWin.noutrefresh()
        self.refreshBody()

    def update_matched(self, match):
        self.match = match
        self.filtered = [n for n in self.data if self.match in n]
        self.setSelection(self.selection)
        self.refreshHead()
        self.refreshBody()

    def refreshHead(self):
        self.headWin.erase()
        self.initHead()

    def refreshBody(self):
        self.bodyWin.erase()
        self.bodyWin.box()

        self.bodyWin.move(1, 1)
        maxDisplay = self.bodyMaxY - 1
        for idx in range(maxDisplay - 1):
            if(idx > maxDisplay):
                break
            try:
                name = self.filtered[idx + self.startPos]
                col = curses.color_pair(5)

                if idx + self.startPos == self.selection:
                    col = curses.color_pair(9)
                    self.bodyWin.hline(idx + 1, 1, ' ', self.bodyMaxX - 2, col)
                elif idx + self.startPos == self.selection:
                    col = curses.color_pair(6)
                    self.bodyWin.hline(idx + 1, 1, ' ', self.bodyMaxX - 2, col)
                self.bodyWin.addstr(idx + 1, 1, name, col)

            except IndexError:
                break

        self.bodyWin.refresh()

    def run(self):
        while True:
            try:
                c = self.bodyWin.getch()
                ret = self.keypress(c)
                if ret:
                    return ret
            except KeyboardInterrupt:
                break

    def setSelection(self, number):
        number = max(0, number)
        number = min(number, len(self.filtered) - 1)

        self.selection = number

        maxDisplayedItems = self.bodyMaxY - 2

        if self.selection - self.startPos >= maxDisplayedItems:
            self.startPos = self.selection - maxDisplayedItems + 1
        elif self.selection < self.startPos:
            self.startPos = self.selection

    def keypress(self, char):
        # FIXME(ja): pageChange should be size of screen!
        pageChange = 5

        if char == 27:  # magic code 'escape' !!!!
            return -1

        if char in (curses.KEY_ENTER, ord('\n'), ord('\r')):
            if len(self.filtered):
                return self.filtered[self.selection]
            else:
                return self.match

        if char == curses.KEY_DOWN:
            self.setSelection(self.selection + 1)
            self.refreshBody()
            return

        if char == curses.KEY_UP:
            self.setSelection(self.selection - 1)
            self.refreshBody()
            return

        if char >= ord('a') and char <= ord('z'):
            self.update_matched(self.match + chr(char))
            self.setSelection(self.selection)
            self.initHead()
            self.refreshBody()
            return

        if char == 263:  # magic code 'backspace' !!!!
            self.update_matched(self.match[:-1])
            return

        if char == curses.KEY_PPAGE:
            self.setSelection(self.selection - pageChange)
            self.refreshBody()
            return

        if char == curses.KEY_NPAGE:
            self.setSelection(self.selection + pageChange)
            self.refreshBody()
            return

        if char == curses.KEY_RESIZE:
            self.setupAndDrawScreen()


def choose(prompt, data):
    c = Chooser(prompt, data)
    return curses.wrapper(c.setup)


if __name__ == '__main__':
    print choose('hmm: ', ['testing', 'one', 'two', 'three'] + ['hmm'] * 100)
    

# pymode:lint_ignore=W901
