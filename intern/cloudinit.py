# helpers for cloud-init

def cloudconfig(options):
    lines = ['#cloud-config']
    if 'ssh_key' in options:
        lines.append('ssh_authorized_keys:\n - %s' % options['ssh_key'])
    if 'packages' in options:
        lines.append('packages:')
        for p in options['packages']:
            lines.append(' - %s' % p)
    if 'apt_proxy' in options:
        lines.append('apt_proxy: %s' % options['apt_proxy'])
    if 'hostname' in options:
        lines.append('hostname: %s' % options['hostname'])
    if options.get('script', None):
        lines.append('runcmd:\n - |')
        for l in options['script'].split('\n'):
            lines.append('  %s' % l)
    return '\n'.join(lines)


