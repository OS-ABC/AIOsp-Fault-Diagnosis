class FaultServiceDetail:
    def __init__(self, faultId: int, serviceName: str, hostName: str, fault_root: str, exception_time: str):
        self.serviceName = serviceName
        self.hostName = hostName
        self.fault_root = fault_root
        self.exception_time = exception_time
        self.faultId = faultId

    def keys(self):
        '''
        当对实例化对象使用dict(obj)的时候, 会调用这个方法,这里定义了字典的键, 其对应的值将以obj['name']的形式取,
        但是对象是不可以以这种方式取值的, 为了支持这种取值, 可以为类增加一个方法
        '''
        return ('serviceName', 'hostName', 'fault_root', 'exception_time', 'faultId')

    def __getitem__(self, item):
        '''
        内置方法, 当使用obj['name']的形式的时候, 将调用这个方法, 这里返回的结果就是值
        '''
        return getattr(self, item)


if __name__ == '__main__':
    a = FaultServiceDetail(1, '2', '3', '4', '5')
    re = dict(a)
    print(re)
