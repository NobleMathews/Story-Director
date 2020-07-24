# ---------------------------------------------------------------------------- #
#                               Helper functions                               #
# ---------------------------------------------------------------------------- #
from dependencies.string_with_arrows import string_with_arrows

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
TT_add='add' # append / replace behaviour
# enhance with following as nested route
TT_process='process'
# 
TT_del='del' # delete behaviour
TT_edit='edit' # view & retrieve to populate UI

# --------------------------------- Commands --------------------------------- #
Commands=['esc','compile']
# bypass tokenizer if the above commands are passed

# ------------------------------ Variable types ------------------------------ #
#  number types for indexes and traversal ||** auto indentified
TT_cmdVar='cmdVar'
TT_cmdFloat='cmdFloat'
TT_cmdIntN='cmdIntN'
TT_cmdInt='cmdInt'
# TT_str all other indetifiers replace string to specific contexts

# [TODO] All of the following are identifiers ||** need to be declared
# which need to be proparly built as nested xml and object keys
# modifier -> identifier -> cmd_var / key
# execution should be nested levels with preserving position in heirarchy to avoid repetition 

# ------------------------------ Story Metadata ------------------------------ #
# [EDIT]
TT_type='type'
#  1) Dialogue 2) Descriptive 3) Tutorials 4) Audio Book
TT_style='style'
#  1) Cartoon (modify search query) 2) Drama (stylize but real humans) 3) Preserve (for testing and for tutorials) 

# ------------------------------ Character Data ------------------------------ #
# [EDIT PROCESS]
TT_cast='cast'

#  [*]
TT_traits='traits'  
#  1) options for specific character traits
TT_face='face'
TT_voice='voice'

# -------------------------------- Story Flow -------------------------------- #
#  [*]
TT_scene='scene'
TT_bg='bg'
TT_choice='choice' # for non linear interactable stories

# -------------------------------- Scene Flow -------------------------------- #
TT_frame='frame'
TT_emotions='emotions'
TT_layer='layer' # frames consist of multiple layers (eg. character describing a place)
TT_lpos='lpos'   # position of a layer in a frame
TT_ldurr='ldur'  # duration for which layer stays in ms

TT_generalCommands=["esc","compile"] 
TT_cmd=["add","process","del","edit"]
TT_identifiers=["type","style","cast","traits","face","voice","scene","bg","choice","frame","emotions","layer","lpos","ldur"]
TT_tokens=TT_cmd+TT_identifiers+TT_generalCommands

TT_EOF='EOF'

class Token:
    def __init__(self,type_,value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value
        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
        if pos_end:
            self.pos_end = pos_end
    
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
    def __init__(self, pos_start, pos_end, error_name,details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name=error_name
        self.details=details

    def as_string(self):
        result  = f'{self.error_name}: {self.details}\n'
        result += f'File {self.pos_start.fn}, line {self.pos_start.ln}'
        result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result

class IllegalParamError(Error):
		def __init__(self, pos_start, pos_end, details):
				super().__init__(pos_start, pos_end, 'Illegal Parameter specified', details)

class InvalidSyntaxError(Error):
		def __init__(self, pos_start, pos_end, details=''):
				super().__init__(pos_start, pos_end, 'Invalid Syntax', details)
        
# ---------------------------------------------------------------------------- #
#                                     Lexer                                    #
# ---------------------------------------------------------------------------- #

class Lexer:
    def __init__(self,fn,text):
        self.fn=fn
        self.preservet=text
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
                pos_temp = self.pos.copy()
                pos_temp.col = len(self.preservet.split(self.current_word)[0])
                tokens.append(Token(self.current_word,pos_start=pos_temp))
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
                pos_a=self.pos.copy()
                pos_b=self.pos.copy()
                unknown = self.current_word
                pre_string=self.preservet.split(unknown)
                pos_a.col=len(pre_string[0])
                pos_start=pos_a
                pos_b.col=len(pre_string[0])+len(unknown)
                pos_end=pos_b
                self.advance()
                return [],IllegalParamError(pos_start,pos_end,"'"+unknown+"'")
            
        pos_temp = self.pos.copy()
        pos_temp.col = len(self.preservet.split(self.current_word)[0])
        tokens.append(Token(TT_EOF,pos_start=pos_temp))
        return tokens, None
    
    def make_cmdVar(self):
        pos_temp = self.pos.copy()
        pos_temp_e= self.pos.copy()
        pos_temp.col = len(self.preservet.split(self.current_word)[0])
        pos_temp_e.col = len(self.preservet.split(self.current_word)[0]) + len(self.current_word)
        cmdVar=self.text[self.pos.idx:]
        cmdVar=" ".join(cmdVar) 
        self.fin()
        return Token(TT_cmdVar,f'{cmdVar}',pos_start=pos_temp,pos_end=pos_temp_e)
    def make_number(self):
        pos_temp = self.pos.copy()
        pos_temp_e= self.pos.copy()
        pos_temp.col = len(self.preservet.split(self.current_word)[0])
        pos_temp_e.col = len(self.preservet.split(self.current_word)[0]) + len(self.current_word)
        dot_count=0
        number=self.current_word
        self.advance()
        if (number).count('.')==1:
            return Token(TT_cmdFloat,float(number),pos_start=pos_temp,pos_end=pos_temp_e)
        elif number[0]=='-':
            return Token(TT_cmdIntN,int(number),pos_start=pos_temp,pos_end=pos_temp_e)
        else:
            return Token(TT_cmdInt,int(number),pos_start=pos_temp,pos_end=pos_temp_e)

# ---------------------------------------------------------------------------- #
#                                    _nodes_                                   #
# ---------------------------------------------------------------------------- #
class generalCommando:
    def __init__(self,tok):
        self.tok=tok
    def __repr__(self):
        return f'{self.tok}'
    
class commandHandler:
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
    
    def fin(self):
        self.tok_idx= len(self.tokens)
        self.advance()
    # generalCommands & modifiers
    # modifiers work on commandvariables which are defined by indentifiers
    def parse(self):
        response=self.generalCommands()

        if(response):
            res = response
        else:
            res=self.identifier()
        
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Undefined identification recieved"
            ))
            
        return res
    
    def generalCommands(self): # relies on nothing else encountering these causes predetermined effect
        tok=self.current_tok
        if tok.type[3:] in TT_generalCommands:
            self.fin()
            return generalCommando(tok)
        else:
            return False
    
    def cmdVar(self): # each should be defined by an identifier
        res = ParseResult()
        tok =self.current_tok
        if tok.type in [TT_cmdVar,TT_cmdFloat,TT_cmdIntN,TT_cmdInt]:
            res.register(self.advance())
            return res.success(commandHandler(tok))
        
        return res.failure(InvalidSyntaxError(
            tok.pos_start,tok.pos_end,"Expected proper command variable to work on"
        ))
    
    def modifier(self): # each should be defined by an identifier
        tok =self.current_tok
        if tok.type[3:] in TT_cmd:
            self.advance()
            return res.success(commandHandler(tok))

    
    def identifier(self): # makes changes in program based on value of command variable and type which it effects
        res=ParseResult()
        modifier = res.register(self.modifier())
        if res.error: return res
        
        while self.current_tok.type[3:] in TT_identifiers:
            identifier=res.register(self.current_tok)
            res.register(self.advance())
            cmdvariable=res.register(self.cmdVar())
            if res.error: return res
            modifier = OperationNode(modifier,identifier,cmdvariable)
        return res.success(modifier)

class ParseResult:
	def __init__(self):
		self.error = None
		self.node = None

	def register(self, res):
		if isinstance(res, ParseResult):
			if res.error: self.error = res.error
			return res.node

		return res

	def success(self, node):
		self.node = node
		return self

	def failure(self, error):
		self.error = error
		return self       

# ---------------------------------------------------------------------------- #
#                                      Run                                     #
# ---------------------------------------------------------------------------- #

def run(fn,text):
    lexer = Lexer(fn, text)
    tokens,error = lexer.make_tokens()
    
    if error:
        return None,error
    # syntax tree for when complex structure
    parser = Parser(tokens)
    # ast = tokens
    ast = parser.parse()
    
    return ast.node,ast.error

