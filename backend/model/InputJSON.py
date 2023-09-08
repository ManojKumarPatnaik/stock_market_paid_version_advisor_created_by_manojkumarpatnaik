class InputJSON:
    def __init__(self, model, messages, max_tokens):
        self.model = model
        self.messages = messages
        self.max_tokens = max_tokens