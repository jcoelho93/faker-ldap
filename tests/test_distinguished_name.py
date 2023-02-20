import unittest
from ldap_provider import DistinguishedName


class TestDistinguishedName(unittest.TestCase):
    def test_distinguished_name(self):
        dn = DistinguishedName([
            ('cn', 'employees'),
            ('ou', 'groups'),
            ('dc', 'example'),
            ('dc', 'org')
        ])

        self.assertEqual(str(dn), "cn=employees,ou=groups,dc=example,dc=org")

    def test_parse_distinguished_name(self):
        dn = "cn=employees,ou=groups,dc=example,dc=org"
        dn_obj = DistinguishedName.parse(dn)

        self.assertEqual(dn_obj.rdn(), ("cn", "employees"))
        self.assertEqual(dn_obj.directories(), [
            ('cn', 'employees'),
            ('ou', 'groups'),
            ('dc', 'example'),
            ('dc', 'org')
        ])


if __name__ == '__main__':
    unittest.main()
