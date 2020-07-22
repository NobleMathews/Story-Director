# ---------------------------------------------------------------------------- #
#                               Helper functions                               #
# ---------------------------------------------------------------------------- #
def RepresentsFloat(s):
    try: 
        float(s)
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
TT_float='TT_float'
TT_nInt='TT_nInt'
TT_int='TT_int'
# TT_str all other indetifiers replace string to specific contexts

# [TODO] All of the following are identifiers ||** need to be declared
# which need to be proparly built as nested xml and object keys
# modifier -> identifier -> cmd_var / key
# execution should be nested levels with preserving position in heirarchy to avoid repetition 

# ------------------------------ Story Metadata ------------------------------ #
# [EDIT]
TT_type='TT_type'
#  1) Dialogue 2) Descriptive 3) Tutorials 4) Audio Book
TT_type='TT_style'
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


class Token:
    def __init__(self,type_,value):
        self.type = type
        self.value = value
    
    def __repr__(self):
        if self.value: return f'{self.type}:{self:value}'
        return f'{self.type}'

# ---------------------------------------------------------------------------- #
#                                     Lexer                                    #
# ---------------------------------------------------------------------------- #

class Lexer:
    def __init__(self,text):
        self.text=text.split()
        self.pos=-1
        self.current_word=None
        self.advance()
    
    def advance(self):
        self.pos+=1
        self.current_word=self.text[pos] if self.pos < len(self.text) else None
    
    def make_tokens(self):
        token=[]
        while self.current_word != None:
            if( globals()[self.current_word]):
                tokens.append(Token(TT_add))
                self.advance()
        return tokens
    
    def make_number(self):
        dot_count=0
        number=self.current_word
        if RepresentsFloat(number):
            if (number).count('.')==1:
                return Token(TT_float)
            elif number[0]=='-':
                return Token(TT_nInt)
            else:
                return Token(TT_int) 
