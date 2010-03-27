END = -1
ERR_UNBALANCED = -2

class Entity:
    def __init__(self, entity):
        self.entity = entity

class OpenTag:
    def __init__(self, tag, rest=''):
        self.tag = tag
        self.rest = rest

    def as_string(self):
        return '<' + self.tag + self.rest + '>'
        
class CloseTag(OpenTag):
    def as_string(self):
        return '</' + self.tag + '>'

class SelfClosingTag(OpenTag):
    pass
    
class Tokenizer:
    def __init__(self, input):
        self.input = input
        self.counter = 0  # points at the next unconsumed character of the input

    def __next_char(self):
        self.counter += 1
        return self.input[self.counter]
        
    def next_token(self):
        try:
            char = self.input[self.counter]
            self.counter += 1
            if char == '&':
                return self.__entity()
            elif char != '<':
                return char
            elif self.input[self.counter] == '/':
                self.counter += 1
                return self.__close_tag()
            else:
                return self.__open_tag()
        except IndexError:
            return END

    def __entity(self):
        """Return a token representing an HTML character entity.
        Precondition: self.counter points at the charcter after the &
        Postcondition: self.counter points at the character after the ;
        """
        char = self.input[self.counter]
        entity = ['&']
        while char != ';':
            entity.append(char)
            char = self.__next_char()
        entity.append(';')
        self.counter += 1
        return Entity( ''.join(entity) )
        
    def __open_tag(self):
        """Return an open/close tag token.
        Precondition: self.counter points at the first character of the tag name
        Postcondition: self.counter points at the character after the <tag>
        """
        char = self.input[self.counter]
        tag = []
        rest = []
        while char != '>' and char != ' ':
            tag.append(char)
            char = self.__next_char()
        while char != '>':
            rest.append(char)
            char = self.__next_char()
        if self.input[self.counter - 1] == '/':
            self.counter += 1
            return SelfClosingTag( ''.join(tag), ''.join(rest) )
        else:
            self.counter += 1
            return OpenTag( ''.join(tag), ''.join(rest) )

    def __close_tag(self):
        """Return an open/close tag token.
        Precondition: self.counter points at the first character of the tag name
        Postcondition: self.counter points at the character after the <tag>
        """
        char = self.input[self.counter]
        tag = []
        while char != '>':
            tag.append(char)
            char = self.__next_char()
        self.counter += 1
        return CloseTag( ''.join(tag) )

def truncate(str, target_len, ellipsis = ''):
    stack = []   # open tags are pushed on here, then popped when the matching close tag is found
    retval = []  # string to be returned
    length = 0   # number of characters (not counting markup) placed in retval so far
    tokens = Tokenizer(str)
    tok = tokens.next_token()
    while tok != END and length < target_len:
        if tok.__class__.__name__ == 'OpenTag':
            stack.append(tok)
            retval.append( tok.as_string() )
        elif tok.__class__.__name__ == 'CloseTag':
            if stack[-1].tag == tok.tag:
                stack.pop()
                retval.append( tok.as_string() )
            else:
                return ERR_UNBALANCED
        elif tok.__class__.__name__ == 'SelfClosingTag':
            retval.append( tok.as_string() )
        elif tok.__class__.__name__ == 'Entity':
            retval.append(tok.entity)
            length += 1
        else:
            retval.append(tok)
            length += 1
        tok = tokens.next_token()
    while len(stack) > 0:
        tok = CloseTag( stack.pop().tag )
        retval.append( tok.as_string() )
    if length == target_len:
        return ''.join(retval) + ellipsis
    else:
        return ''.join(retval)        
