import argparse
from db_settings import *

# class User(Base):
#     __tablename__ = 'users'
#     id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
#     username = Column(String(50), unique=True)
#     email = Column(String(50))

#     def __repr__(self):
#         return "<User(username='%s', email='%s')>" % (
#             self.username, self.email)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--migrate', action='store_true')
    args = parser.parse_args()

    if args.migrate:
        migrate()

    # migrate()
    # user = User(username='admin',email = 'admin@gmail.com')
    # session.add(user)
    # session.commit()
    # user = session.query(User).first()
    # print(user)