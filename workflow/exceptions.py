
class WorkflowError(Exception): pass

class TokenAlreadyConsumed(WorkflowError): pass

class TokenRequired(WorkflowError): pass