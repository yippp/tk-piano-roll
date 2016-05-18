from Tkinter import *
from src.helper import isint


class CustomSpinbox(Spinbox):

    def __init__(self, *args, **kwargs):
        start = kwargs.pop('start', None)
        Spinbox.__init__(self, *args, **kwargs)

        self._init_data(str(start))
        self._bind_event_handlers()

    def _init_data(self, start):
        from_ = str(int(self.config()['from'][4]))
        self._curr_value = start if start else from_
        self._prev_value = self._curr_value

        self._var = StringVar(self)
        self._var.set(from_)
        self._var.trace('w', self._update)
        self.config(textvariable=self._var, state='readonly')
        self.set(self._curr_value)

        self._on_value_change = lambda: None

    def _update(self, *args):
        self._curr_value = self._var.get()

    def _bind_event_handlers(self):
        self.bind('<Return>', self._on_return)
        self.bind('<KP_Enter>', self._on_return)
        # self.bind('<FocusOut>', self._on_lost_focus)
        self.bind('<Key>', self._after_keypress)

    def _on_return(self, event):
        state = self.config()['state'][4]
        if state == 'readonly':
            self.config(state='normal')
        else:
            value = self._validate()
            self._curr_value = value
            self._prev_value = self._curr_value
            self._var.set(self._curr_value)
            self._on_value_change()
            self.config(state='readonly')

    def _on_lost_focus(self, event):
        state = self.config()['state'][4]
        if state == 'normal':
            self.config(state='readonly')
            self.selection_clear()

            value = self._validate()
            self._curr_value = value
            self._var.set(self._curr_value)
            self._on_value_change()

    def _after_keypress(self, event):
        self.after_idle(self.icursor, END)

    def _validate(self):
        if isint(self._curr_value):
            value = int(self._curr_value)
            to = int(self.config()['to'][4])
            from_ = int(self.config()['from'][4])

            if value < from_:
                value = from_
            elif value > to:
                value = to
        else:
            value = self._prev_value

        return str(value)

    def set(self, value):
        self._var.set(value)
        self._update()

    def set_from(self, from_):
        if self._curr_value < from_:
            self._curr_value = str(from_)
        self.config(from_=from_)

    def set_to(self, to):
        if self._curr_value > to:
            self._curr_value = str(to)
        self.config(to=to)

    def on_value_change(self, callback):
        self._on_value_change = callback
        self.config(command=self._on_value_change)