from typing import List, Tuple
from faker import Faker
from faker.providers import BaseProvider


faker: Faker = Faker()


class DistinguishedName:
    def __init__(self, directories: List[Tuple]):
        self._directories = directories

    @classmethod
    def parse(cls, raw):
        components = raw.split(",")
        directories = []
        for component in components:
            attr = component.split("=")[0]
            value = component.split("=")[1]
            directories.append(
                (attr, value)
            )
        return cls(directories)

    def rdn(self) -> str:
        return self._directories[0]

    def directories(self) -> List[Tuple]:
        return self._directories

    def __str__(self) -> str:
        dn = []
        for directory in self._directories:
            dn.append("%s=%s" % directory)
        return ','.join(dn)


class LDAPUser:
    def __init__(self, dn: DistinguishedName, first_name: str, last_name: str):
        self.dn = dn
        self.cn = dn.rdn()
        self.uid = self.cn[1]
        self.given_name = first_name
        self.sn = last_name
        self.home_directory = f"/home/{self.uid}"
        self.object_classes = ["inetOrgPerson", "posixAccount", "top"]
        self.uid_number = faker.random_number()

    def ldif(self):
        ldif = [
            "dn: %s" % self.dn,
            "cn: %s" % self.cn[1],
            "uid: %s" % self.uid,
            "givenname: %s" % self.given_name,
            "sn: %s" % self.sn,
            "homedirectory: %s" % self.home_directory,
            "uidnumber %s" % self.uid_number,
        ]
        for cls in self.object_classes:
            ldif.append(
                "objectclass: %s" % cls
            )
        return '\n'.join(ldif)


class LDAPGroup:
    def __init__(self, dn: DistinguishedName, member: str) -> None:
        self.dn = dn
        self.cn = self.dn.rdn()
        self.member = member

    def ldif(self):
        ldif = [
            "dn: %s" % self.dn,
            "cn: %s" % self.cn[1],
            "objectclass: groupOfNames",
            "objectclass: top",
            "description: %s" % faker.sentence(nb_words=10),
            "member: %s" % self.member,
            "owner: %s" % self.member
        ]
        return '\n'.join(ldif)


class LDAPProvider(BaseProvider):
    def object_class(self) -> str:
        classes = [
            "accessControlSubentry",
            "account",
            "alias",
            "applicationEntity",
            "applicationProcess",
            "bootableDevice",
            "certificationAuthority",
            "certificationAuthority-V2",
            "collectiveAttributeSubentry",
            "country",
            "crlDistributionPoint",
            "device",
            "dmd",
            "dnsDomain",
            "documentSeries",
            "domain",
            "domainRelatedObject",
            "dsa",
            "extensibleObject",
            "friendlyCountry",
            "groupOfNames",
            "groupOfUniqueNames",
            "ieee802Device",
            "inetOrgPerson",
            "ipHost",
            "ipNetwork",
            "ipProtocol",
            "ipService",
            "locality",
            "mailRecipient",
            "newPilotPerson",
            "nisDomainObject",
            "nisKeyObject",
            "nisMap",
            "nisNetgroup",
            "nisObject",
            "organization",
            "organizationalPerson",
            "organizationalRole",
            "organizationalUnit",
            "person",
            "posixAccount",
            "posixGroup",
            "room",
            "strongAuthenticationUser"
        ]
        return faker.random.choice(classes)

    def group_dn(self, domain: str = None, base_dn: str = 'ou=groups', common_name: str = None) -> str:
        if not domain:
            domain = self.domain()
        if not common_name:
            common_name = faker.word()
        dn = f"cn={common_name},{base_dn},{domain}"
        dn = DistinguishedName.parse(dn)
        return str(dn)

    def user_dn(self, domain: str = None, base_dn: str = 'ou=users') -> str:
        if not domain:
            domain = self.domain()
        uid = faker.simple_profile().get('username')
        dn = f"cn={uid},{base_dn},{domain}"
        dn = DistinguishedName.parse(dn)
        return str(dn)

    def user_ldif(self):
        user = LDAPUser(
            DistinguishedName.parse(self.user_dn()),
            faker.first_name(),
            faker.last_name()
        )
        return user.ldif()

    def group_ldif(self, domain: str = None):
        member = self.user_dn('dc=example,dc=org')
        group = LDAPGroup(
            DistinguishedName.parse(self.group_dn(domain=domain)),
            member
        )
        return group.ldif()

    def unique_groups(self, seed_names: List[str], domain: str = 'dc=example,dc=org') -> List[LDAPGroup]:
        groups = []
        for name in seed_names:
            dn = self.group_dn(domain=domain, common_name=name)
            member = self.user_dn(domain=domain)
            groups.append(LDAPGroup(DistinguishedName.parse(dn), member))
        return groups

    def domain(self) -> str:
        domain_name = faker.domain_name()
        name, tld = domain_name.split(".")
        return "dc=%s,dc=%s" % (name, tld)
