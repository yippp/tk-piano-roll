from observer import Observer


def notifiable(mask=None):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            if self._ntflag:
                self.notify(mask)
            if mask:
                self._altmask |= mask
            return result
        return wrapper
    return decorator


class Observable(object):

    def __init__(self):
        self._observers = []
        self._ntflag = True
        self._altmask = 0

    @property
    def observers(self):
        return list(self._observers)

    @property
    def is_notifying(self):
        return self._ntflag

    def register_observer(self, callable, knowledge=None):
        if not hasattr(callable, '__call__'):
            raise ValueError("{0} instance has no"
                " __call__ method".format(
                callable.__class__.__name__))

        self._observers.append(Observer(callable, knowledge))

    def unregister_observer(self, callable):
        self._observers.remove(callable)

    def notify(self, mask=None):
        if mask:
            observers = [obs for obs in self.observers if
                obs.knowledge & mask > 0]
        else:
            observers = self.observers

        for observer in observers:
            vargs, kwargs = self.response(observer.knowledge)
            observer(*vargs, **kwargs)

    def response(self, knowledge=None):
        pass

    def enable_notifications(self):
        self._ntflag = True
        self.notify(self._altmask)

    def disable_notifications(self):
        if self._ntflag:
            self._ntflag = False
            self._altmask = 0
