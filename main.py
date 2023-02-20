from faker import Faker
from ldap_provider import LDAPProvider


fake = Faker()
fake.add_provider(LDAPProvider)

seed_names = [fake.unique.word() for i in range(963)]
groups = fake.unique_groups(seed_names)

with open('bootstrap.ldif', mode='w') as fp:
    for group in groups:
        fp.write(group.ldif())
        fp.write("\n")
        fp.write("\n")
