
class WorkflowError(Exception): pass

class TokenAlreadyConsumed(WorkflowError): pass

class TokenRequired(WorkflowError): pass

class TokenRejected(WorkflowError): pass

class BadActivity(WorkflowError): pass