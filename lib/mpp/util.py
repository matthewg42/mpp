import logging

log = logging.getLogger('mpp')

def confirm(prompt='Confirm?', def_yes=False):
    if def_yes:
        prompt += ' [Y/n] > '
    else:
        prompt += ' [y/N] > '
    
    while True:
        resp = input(prompt)
        if not resp:
            return def_yes
        if resp not in ['y', 'Y', 'n', 'N']:
            print('please enter y or n.')
            continue
        if resp.lower() == 'y':
            return True
        if resp.lower() == 'n':
            return False

def update_and_save_podcast(p):
    log.debug('update_and_save_podcast(%s) starting' % p.title)
    new = p.update()
    log.debug('update_and_save_podcast(%s) %d new episodes' % (p.title, new))
    if new > 0:
        log.debug('update_and_save_podcast(%s) saving' % p.title)
        p.save()
    
