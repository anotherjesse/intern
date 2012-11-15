# helpers for cloud-init

def cloudconfig(options):
    lines = ['#cloud-config']
    if options.get('apt_proxy'):
        lines.append('apt_proxy: %s' % options['apt_proxy'])
    if options.get('root'):
        lines.append('disable_root: False')
    if options.get('hostname'):
        lines.append('hostname: %s' % options['hostname'])
    if options.get('packages'):
        lines.append('packages:')
        for p in options['packages']:
            lines.append(' - %s' % p)
    if options.get('script', None):
        lines.append('runcmd:\n - |')
        for l in options['script'].split('\n'):
            lines.append('  %s' % l)
    if options.get('ssh_key'):
        lines.append('ssh_authorized_keys:\n - %s' % options['ssh_key'])
    return '\n'.join(lines)


