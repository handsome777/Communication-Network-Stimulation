from Queue import PriorityQueue
class node():
    def __init__(self, p_addr, cost, addr):
        self.p_addr = p_addr
        self.cost = cost
        self.addr = addr
    def __lt__(self, other):
        return self.cost < other.cost

Q = PriorityQueue()
Q.put(node(5, 2, 0))
Q.put(node(5, 1, 1))
Q.put(node(0, 0, 1))
n1  = Q.get()
print n1.p_addr,n1.cost,n1.addr

k = ["1","2"]
n = "aaa"
if n not in k:
	print "s"