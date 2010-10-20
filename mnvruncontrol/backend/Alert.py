import uuid

WARNING = 1
ERROR = 2

DESCRIPTIONS = { WARNING : "Warning",
                 ERROR   : "Error" }


class Alert:
	""" Used internally for storing and communicating alerts to clients. """
	
	def __init__(self, notice=None, severity=WARNING, manager=False):
		if severity not in (WARNING, ERROR):
			raise TypeError("'severity' must be either WARNING or ERROR.")
			
		self.id = uuid.uuid4()
		self.notice = notice
		self.severity = severity
		self.is_manager_alert = manager
	
	def __eq__(self, other):
		if isinstance(other, uuid.UUID):
			return self.id == other
		
		if not hasattr(other, "id"):
			return False
		
		return self.id == other.id
		
	def __repr__(self):
		return "(%s, %s, %s, from manager=%s)" % (self.id, DESCRIPTIONS[self.severity], self.notice, self.is_manager_alert)

