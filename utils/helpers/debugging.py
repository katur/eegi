'''
import datetime
print 'before'
net = 0
    start = datetime.datetime.now()
    end = datetime.datetime.now()
    elapsed = end - start
    net += elapsed.microseconds
print 'after: {}'.format(net)
'''
