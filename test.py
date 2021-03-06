import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest
from SaltGenResource import ResourceGenerator

class TestMapping(unittest.TestCase):

    def test_os_family_map1(self):
        os_family = ResourceGenerator._os_family('Linux')
        self.assertEqual(os_family, 'unix')

    def test_os_family_map2(self):
        os_family = ResourceGenerator._os_family('unknown')
        self.assertEqual(os_family, 'unknown')

    def test_os_arch_map1(self):
        os_arch = ResourceGenerator._os_arch('x86_64')
        self.assertEqual(os_arch, 'amd64')

    def test_os_arch_map2(self):
        os_arch = ResourceGenerator._os_arch('unknown')
        self.assertEqual(os_arch, 'unknown')

class TestNodeGenerator(unittest.TestCase):

    _base_args = ['-l', 'quiet']
    required_attributes = ['hostname', 'osArch', 'osFamily',
                           'osName', 'osVersion']

    def test_glob_targeting(self):
        args = self._base_args + ['*']
        resources = ResourceGenerator(args).run()
        self._test_attributes(resources, self.required_attributes)

    def test_cidr_targeting(self):
        args = self._base_args + ['-S', '0.0.0.0/0']
        resources = ResourceGenerator(args).run()
        self._test_attributes(resources, self.required_attributes)

    def test_grain_targeting(self):
        args = self._base_args + ['-G', 'os:*']
        resources = ResourceGenerator(args).run()
        self._test_attributes(resources, self.required_attributes)

    def test_pcre_targeting(self):
        args = self._base_args + ['-E', '.*']
        resources = ResourceGenerator(args).run()
        self._test_attributes(resources, self.required_attributes)

    def test_grain_pcre_targeting(self):
        args = self._base_args + ['-P', 'os:.*']
        resources = ResourceGenerator(args).run()
        self._test_attributes(resources, self.required_attributes)

    def test_single_attribute(self):
        optional_attributes = ['os']
        args = self._base_args + ['-a', optional_attributes[0], '*']
        resources = ResourceGenerator(args).run()
        self._test_attributes(resources, self.required_attributes)
        self._test_attributes(resources, optional_attributes)

    def test_multiple_attributes1(self):
        optional_attributes = ['os', 'os_family']
        args = self._base_args + ['-a', ' '.join(optional_attributes), '*']
        resources = ResourceGenerator(args).run()
        self._test_attributes(resources, self.required_attributes)
        self._test_attributes(resources, optional_attributes)

    def test_multiple_attributes2(self):
        optional_attributes = ['os', 'os_family']
        args = self._base_args + ['-a', ','.join(optional_attributes), '*']
        resources = ResourceGenerator(args).run()
        self._test_attributes(resources, self.required_attributes)
        self._test_attributes(resources, optional_attributes)

    def test_single_tag(self):
        tags = ['os']
        args = self._base_args + ['-t', tags[0], '*']
        resources = ResourceGenerator(args).run()
        self._test_attributes(resources, self.required_attributes)
        self._test_tags(resources, tags)

    def test_multiple_tags1(self):
        tags = ['os', 'os_family']
        args = self._base_args + ['-t', ' '.join(tags), '*']
        resources = ResourceGenerator(args).run()
        self._test_attributes(resources, self.required_attributes)
        self._test_tags(resources, tags)

    def test_multiple_tags1(self):
        tags = ['os', 'os_family']
        args = self._base_args + ['-t', ','.join(tags), '*']
        resources = ResourceGenerator(args).run()
        self._test_attributes(resources, self.required_attributes)
        self._test_tags(resources, tags)

    def test_static_attributes(self):
        args = self._base_args + ['*', 'username=root', 'password=\'pw\'']
        resources = ResourceGenerator(args).run()
        self._test_attributes(resources, self.required_attributes)
        self._test_attributes(resources, ['username', 'password'])

    def _test_attributes(self, resources, needed):
        self.assertTrue(len(resources) > 0)
        for host, attributes in resources.iteritems():
            for attribute in needed:
                self.assertIn(attribute, attributes)
                self.assertIsNotNone(attributes[attribute])
                self.assertNotEqual(attributes[attribute], '')

    def _test_tags(self, resources, needed):
        self.assertTrue(len(resources) > 0)
        for host, attributes in resources.iteritems():
            self.assertIn('tags', attributes)
            self.assertIsNotNone(attributes['tags'])
            self.assertTrue(len(attributes['tags']) >= len(needed))

class TestServerNodeGenerator(TestNodeGenerator):
    _base_args = TestNodeGenerator._base_args + ['--include-server-node']

    def _test_attributes(self, resources, needed):
        super(TestServerNodeGenerator, self)._test_attributes(resources, needed)
        self.assertIn(ResourceGenerator._server_node_name, resources)
        self.assertEqual(
            resources[ResourceGenerator._server_node_name]['hostname'],
            ResourceGenerator._server_node_name)

if __name__ == '__main__':
    runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=2)
    unittest.main(testRunner=runner, buffer=True)
