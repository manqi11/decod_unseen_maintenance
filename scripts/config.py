import sys
sys.path.insert(0, './')

import os
import os.path as op

# Experiment parameters
open_browser = True
base_path = op.dirname(op.dirname(__file__))
print base_path
data_path = op.join(base_path, 'data/')
# XXX what to do with this ad hoc paths?
# script_path = '/home/niccolo/Dropbox/DOCUP/scripts/python/'
# pyoutput_path = op.join(base_path, '/media', 'niccolo', 'ParisPy', 'data')


def paths(typ, subject='fsaverage', data_type='erf', lock='target',
          analysis='analysis', pyscript='config.py', log=False):
    # FIXME: cleanup epochs filenames
    this_path = op.join(data_path, subject, typ)
    path_template = dict(
        base_path=base_path,
        data_path=data_path,
        report=op.join(base_path, 'results'),
        log=op.join(base_path, pyscript.strip('.py') + '.log'),

        behavior=op.join(this_path, '%s_fixed.mat' % subject),
        epoch=op.join(this_path, '%s_%s_%s.mat' % (subject, lock, data_type)),
        evoked=op.join(this_path, '%s_%s_%s_%s.pickle' % (
            subject, lock, data_type, analysis)),
        decod=op.join(this_path, '%s_%s_%s_%s.pickle' % (
            subject, lock, data_type, analysis)),
        generalize=op.join(this_path, '%s_%s_%s_%s.pickle' % (
            subject, lock, data_type, analysis)))
    file = path_template[typ]

    # Log file ?
    if log:
        fname = paths('log')
        print '%s: %s ' % (fname, file)
        with open(fname, "a") as myfile:
            myfile.write("%s \n" % file)

    # Create subfolder if necessary
    folder = os.path.dirname(file)
    folder_ = folder.split('/') if folder != '' else []
    for ii in range(len(folder_)):
        if not op.exists(folder_[0]):
            os.mkdir(folder_[0])
        if len(folder_) > 1:
            folder_ = [folder_[0] + '/' + folder_[1]] + folder_[2:]

    return file

subjects = [
    'ak130184', 'el130086', 'ga130053', 'gm130176', 'hn120493',
    'ia130315', 'jd110235', 'jm120476', 'ma130185', 'mc130295',
    'mj130216', 'mr080072', 'oa130317', 'rg110386', 'sb120316',
    'tc120199', 'ts130283', 'yp130276', 'av130322', 'ps120458']

# Define type of sensors used (useful for ICA correction, plotting etc)
from mne.channels import read_ch_connectivity
meg_connectivity, _ = read_ch_connectivity('neuromag306mag')
chan_types = [dict(name='meg', connectivity=meg_connectivity)]

# Decoding preprocessing steps
preproc = dict()

# ###################### Define contrasts #####################
from orientations.conditions import analyses

# #############################################################################
# univariate analyses definition: transform the input used for the decoding to
# the univariate analyse. Yes this NEEDS to be cleaned
# from analyses_definition_univariate import format_analysis
# analyses = [format_analysis(contrast) for contrast in contrasts]

# ############## Define type of input (erf,frequenct etc...) ##################
data_types = ['erf'] + ['freq%s' % f for f in [7, 10, 12, 18, 29, 70, 105]]

# ##################################""
# # UNCOMMENT TO SUBSELECTION FOR FAST PROCESSING
# #
# subjects = [subjects[1]]
data_types = [data_types[0]]
# analyses = [ana for ana in analyses if ana['name'] == 'target_circAngle']
preproc = dict(decim=2, crop=dict(tmin=-.2, tmax=1.200))
# preproc = dict(decim=2, crop=dict(tmin=-.1, tmax=1.100))
