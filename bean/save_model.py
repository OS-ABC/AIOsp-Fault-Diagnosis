from sqlalchemy import Column, Integer, Text, DateTime, Date, String,text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class FaultService(Base):
    __tablename__ = 'fault_service'
    id = Column(Integer, primary_key=True)
    fault_service_id = Column(String)
    fault_service_name = Column(String)
    fault_service_type = Column(String)
    host_name = Column(String)
    exception_time = Column(DateTime)
    process_state = Column(Integer)
    create_time = Column(DateTime,server_default=text('CURRENT_TIMESTAMP'))
    update_time = Column(DateTime,server_default=text('CURRENT_TIMESTAMP'))
    __mapper_args__ = {
        "order_by": create_time.desc()
    }

    def to_dict(self):
        return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}

class FaultServiceRoot(Base):
    __tablename__ = 'fault_service_root_detail'
    id = Column(Integer, primary_key=True)
    fault_id = Column(Integer)
    causeOfFault = Column(String)
    causeName = Column(String)
    detail = Column(Text)
    has_solution = Column(Integer)
    type = Column(Integer) #0:指标
    rank = Column(Integer) #1 2 3
    create_time = Column(DateTime,server_default=text('CURRENT_TIMESTAMP'))
    update_time = Column(DateTime,server_default=text('CURRENT_TIMESTAMP'))
    __mapper_args__ = {
        "order_by": create_time.desc()
    }

    def to_dict(self):
        return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}

class ServiceDependencyGraph(Base):
    __tablename__ = 'service_dependency_graph'
    id = Column(Integer, primary_key=True)
    fault_id = Column(Integer)
    graph_json = Column(Text)
    create_time = Column(DateTime,server_default=text('CURRENT_TIMESTAMP'))
    update_time = Column(DateTime,server_default=text('CURRENT_TIMESTAMP'))
    __mapper_args__ = {
        "order_by": create_time.desc()
    }

    def to_dict(self):
        return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}
class ExceptionDataDependencyGraph(Base):
    __tablename__ = 'exception_data_dependency_graph'
    id = Column(Integer, primary_key=True)
    fault_id = Column(Integer)
    graph_json = Column(Text)
    create_time = Column(DateTime,server_default=text('CURRENT_TIMESTAMP'))
    update_time = Column(DateTime,server_default=text('CURRENT_TIMESTAMP'))
    __mapper_args__ = {
        "order_by": create_time.desc()
    }

    def to_dict(self):
        return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}

class FaultServiceSolution(Base):
    __tablename__ = 'fault_service_solution'
    id = Column(Integer, primary_key=True)
    fault_id = Column(Integer)
    root_log_id = Column(String)
    fault_reason = Column(Text)
    fault_solution = Column(Text)
    rank = Column(Integer)  # 1 2 3
    create_time = Column(DateTime,server_default=text('CURRENT_TIMESTAMP'))
    update_time = Column(DateTime,server_default=text('CURRENT_TIMESTAMP'))
    __mapper_args__ = {
        "order_by": create_time.desc()
    }

    def to_dict(self):
        return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}
