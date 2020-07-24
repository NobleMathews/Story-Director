# ---------------------------------------------------------------------------- #
#                               Helper functions                               #
# ---------------------------------------------------------------------------- #
def RepresentsFloat(s):
    try: 
        float(s)
        return True
    except ValueError:
        return False
def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False
# ---------------------------------------------------------------------------- #
#                                    Tokens                                    #
# ---------------------------------------------------------------------------- #

# --------------------------------- Modifiers -------------------------------- #
TT_add='TT_add' # append / replace behaviour
# enhance with following as nested route
TT_process='TT_process'
# 
TT_del='TT_del' # delete behaviour
TT_edit='TT_edit' # view & retrieve to populate UI

# --------------------------------- Commands --------------------------------- #
Commands=['esc','compile']
# bypass tokenizer if the above commands are passed

# ------------------------------ Variable types ------------------------------ #
#  number types for indexes and traversal ||** auto indentified
TT_cmdVar='TT_cmdVar'
TT_cmdFloat='TT_cmdFloat'
TT_cmdIntN='TT_cmdIntN'
TT_cmdInt='TT_cmdInt'
# TT_str all other indetifiers replace string to specific contexts

# [TODO] All of the following are identifiers ||** need to be declared
# which need to be proparly built as nested xml and object keys
# modifier -> identifier -> cmd_var / key
# execution should be nested levels with preserving position in heirarchy to avoid repetition 

# ------------------------------ Story Metadata ------------------------------ #
# [EDIT]
TT_type='TT_type'
#  1) Dialogue 2) Descriptive 3) Tutorials 4) Audio Book
TT_style='TT_style'
#  1) Cartoon (modify search query) 2) Drama (stylize but real humans) 3) Preserve (for testing and for tutorials) 

# ------------------------------ Character Data ------------------------------ #
# [EDIT PROCESS]
TT_cast='TT_cast'

#  [*]
TT_traits='TT_traits'  
#  1) options for specific character traits
TT_face='TT_face'
TT_voice='TT_voice'

# -------------------------------- Story Flow -------------------------------- #
#  [*]
TT_scene='TT_scene'
TT_bg='TT_bg'
TT_choice='TT_choice' # for non linear interactable stories

# -------------------------------- Scene Flow -------------------------------- #
TT_frame='TT_frame'
TT_emotions='TT_emotions'
TT_layer='TT_layer' # frames consist of multiple layers (eg. character describing a place)
TT_lpos='TT_lpos'   # position of a layer in a frame
TT_ldurr='TT_ldur'  # duration for which layer stays in ms

TT_cmd=["esc","compile","add","process","del","edit"]
TT_identifiers=["type","style","cast","traits","face","voice","scene","bg","choice","frame","emotions","layer","lpos","ldur"]
TT_tokens=TT_cmd+TT_identifiers

class Token:
    def __init__(self,type_,value=None):
        self.type = type_
        self.value = value
    
    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'

# ---------------------------------------------------------------------------- #
#                                 Error Details                                #
# ---------------------------------------------------------------------------- #

class Position:
    def __init__(self,idx,ln,col,fn,ftxt):
        self.idx=idx
        self.ln=ln
        self.col=col
        self.fn=fn
        self.ftxt=ftxt
    
    def advance(self):
        self.idx += 1
        self.col += 1
        
        if self.idx ==  0:
            self.ln+=1
            self.col=0
        
        return self
    
    def copy(self):
        return Position(self.idx,self.ln,self.col,self.fn,self.ftxt)

# ---------------------------------------------------------------------------- #
#                                     Error                                    #
# ---------------------------------------------------------------------------- #

class Error:
    def __init__(self,pos_e,error_name,details):
        self.pos_e=pos_e
        self.error_name=error_name
        self.details=details
    def __str__(self):
        result = ''+str(self.error_name)+' : '+str(self.details)+ ' '
        result += f'[ File {self.pos_e.fn}, Line {self.pos_e.ln},Pos: {self.pos_e.col+1} ]'
        return result

class IllegalParamError(Error):
    def __init__(self,pos_e,details):
        super().__init__(pos_e,'Illegal Parameter specified',details)
        
# ---------------------------------------------------------------------------- #
#                                     Lexer                                    #
# ---------------------------------------------------------------------------- #

class Lexer:
    def __init__(self,fn,text):
        self.fn=fn
        self.text=text.split()
        self.pos=Position(-1,0,-1,fn,text)
        self.current_word=None
        self.advance()
    
    def advance(self):
        self.pos.advance()
        self.current_word=self.text[self.pos.idx] if self.pos.idx < len(self.text) else None
    
    def fin(self):
        self.pos.idx= len(self.text)
        self.advance()
    
    def make_tokens(self):
        tokens=[]
        while self.current_word != None:
            if RepresentsFloat(self.current_word) or RepresentsInt(self.current_word):
                tokens.append(self.make_number())
            elif self.current_word in TT_tokens:
                tokens.append(Token("TT_"+self.current_word))
                if self.current_word in TT_identifiers:
                    self.advance()
                    if self.current_word != None:
                        if RepresentsFloat(self.current_word) or RepresentsInt(self.current_word):
                            tokens.append(self.make_number())
                        else:
                            tokens.append(self.make_cmdVar())
                else:                
                    self.advance()
            else:
                pos_e=self.pos.copy()
                unknown = self.current_word 
                self.advance()
                return [],IllegalParamError(pos_e,"'"+unknown+"'")
        return tokens, None
    
    def make_cmdVar(self):
        cmdVar=self.text[self.pos.idx:]
        cmdVar=" ".join(cmdVar) 
        self.fin()
        print(Token(TT_cmdVar,f'{cmdVar}'))
        return Token(TT_cmdVar,f'{cmdVar}')
    def make_number(self):
        dot_count=0
        number=self.current_word
        self.advance()
        if (number).count('.')==1:
            return Token(TT_cmdFloat,float(number))
        elif number[0]=='-':
            return Token(TT_cmdIntN,int(number))
        else:
            return Token(TT_cmdInt,int(number))

# ---------------------------------------------------------------------------- #
#                                    _nodes_                                   #
# ---------------------------------------------------------------------------- #
class CmdVar:
    def __init__(self,tok):
        self.tok=tok
    def __repr__(self):
        return f'{self.tok}'

class OperationNode:
    def __init__(self,left_node,op_token,right_node):
        self.left_node = left_node
        self.op_token = op_token
        self.right_node = right_node
    
    def __repr__(self):
        return f'[{self.left_node},{self.op_token},{self.right_node}]'

# ---------------------------------------------------------------------------- #
#                                    Parser                                    #
# ---------------------------------------------------------------------------- #

class Parser:
    def __init__(self,tokens):
        self.tokens=tokens
        self.tok_idx=-1
        self.advance()
        
    def advance(self):
        self.tok_idx+=1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok
        

# ---------------------------------------------------------------------------- #
#                                      Run                                     #
# ---------------------------------------------------------------------------- #

def run(fn,text):
    lexer = Lexer(fn, text)
    tokens,error = lexer.make_tokens()
    
    return tokens,error

