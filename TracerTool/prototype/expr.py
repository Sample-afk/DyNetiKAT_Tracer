from enum import Enum, auto

class Expr:
    class PartType(Enum):
        PACKET_MANIPULATION = auto()
        SEND = auto()
        RECEIVE = auto()
        
    class ExprPart:
        def __init__(self, type, msg, sender, channel=None) -> None:
            self.type = type
            self.msg = msg
            self.sender = sender
            self.channel = channel
        
        def __repr__(self) -> str:
            return (f"ExprPart(type={self.type.name}, msg='{self.msg}', "
                    f"sender={self.sender}, receiver={self.channel})")
            
    def __init__(self, string_expr) -> None:
        pass
    
    def convert(self, string):
        start = 0
        string.find(';', start)
        string.find('o+', start)
        
        
        # [; ; ; ] o+ []