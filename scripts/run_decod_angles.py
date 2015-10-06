import pickle
import numpy as np
from jr.stats import circ_tuning, circ_mean, repeated_spearman
from scripts.config import paths, subjects, subscores, analyses
from base import get_predict, get_predict_error, angle_acc
analyses = [analysis for analysis in analyses if analysis['name'] in
            ['target_circAngle', 'probe_circAngle']]

tois = [(-.100, 0.050), (.100, .250), (.300, .800), (.900, 1.050)]


# Gather data
for analysis in ['target_circAngle', 'probe_circAngle']:
    results = dict(diagonal=list(), angle_pred=list(), toi=list(),
                   subscore=list(), corr_contrast=list(), corr_pas=list(),
                   R_contrast=list(), R_vis=list(), align_on_diag=list(),
                   early_maintain=list(), R_vis_duration=list())
    for s, subject in enumerate(subjects):
        # load data
        print s
        fname = paths('decod', subject=subject, analysis=analysis)
        with open(fname, 'rb') as f:
            gat, _, events_sel, events = pickle.load(f)
        times = gat.train_times_['times']
        subevents = events.iloc[events_sel].reset_index()
        n_bins = 24

        # Mean error across trial on the diagonal
        y_error = angle_acc(get_predict_error(gat, mean=False), axis=0)
        results['diagonal'].append(y_error)

        # Mean prediction for each angle at peak time
        toi = [.100, .250] if analysis == 'target_circAngle' else [.900, 1.150]
        results_ = list()
        for angle in np.unique(gat.y_true_):
            y_pred = get_predict(gat, sel=np.where(gat.y_true_ == angle)[0],
                                 toi=toi)
            probas, bins = circ_tuning(y_pred, n=n_bins)
            results_.append(probas)
        results['angle_pred'].append(results_)

        # Mean tuning error per toi
        results_ = list()
        for toi in tois:
            probas, bins = circ_tuning(get_predict_error(gat, toi=toi),
                                       n=n_bins)
            results_.append(probas)
        results['toi'].append(results_)

        # Mean y_error per toi per vis
        results_ = dict()
        y_error = get_predict_error(gat, mean=False)
        for subanalysis in subscores:
            results_[subanalysis[0] + '_toi'] = list()
            # subselect events (e.g. seen vs unseen)
            subsel = subevents.query(subanalysis[1]).index
            # add nan if no trial matches subconditions
            if len(subsel) == 0:
                results_[subanalysis[0]] = np.nan * np.zeros(y_error.shape[1])
                for toi in tois:
                    results_[subanalysis[0] + '_toi'].append(np.nan)
                continue
            # dynamics of mean error
            results_[subanalysis[0]] = angle_acc(y_error[subsel, :], axis=0)
            # mean error per toi
            for toi in tois:
                # mean error across time
                toi_ = np.where((times >= toi[0]) & (times < toi[1]))[0]
                y_error_toi = circ_mean(y_error[:, toi_], axis=1)
                y_error_toi = angle_acc(y_error_toi[subsel])
                results_[subanalysis[0] + '_toi'].append(y_error_toi)
        results['subscore'].append(results_)

        # Duration
        results_ = list()
        R_vis_duration = list()
        for toi in tois:
            # for each toi: 1. realign pred on diag, 2. compute error
            y_error = get_predict_error(gat, toi=toi, typ='align_on_diag',
                                        mean=False)
            results_pas = list()
            for pas in range(4):
                # select condition
                pas_cond = 'detect_button == %i' % pas
                present_cond = ' and target_present == True'
                sel = subevents.query(pas_cond + present_cond).index
                # if no trial matches seleted conditions, add NaNs
                if len(sel) == 0:
                    results_pas.append(np.nan * np.zeros(y_error.shape[2]))
                    continue
                # 3. mean error across trials
                y_error_ = angle_acc(y_error[sel, ...], axis=0)
                # 4. mean across classifier (toi)
                y_error_ = np.mean(y_error_, axis=0)
                results_pas.append(y_error_)
            results_.append(results_pas)
            # Finally, test if duration if affected by visibility :
            sel = subevents.query('target_present == True').index
            # mean clf R in TOI
            X = angle_acc(y_error[sel, :, :], axis=1)
            R = repeated_spearman(X.reshape([len(sel), -1]),
                                  np.array(subevents['detect_button'][sel]))
            R_vis_duration.append(R.reshape(y_error.shape[2]))
        results['align_on_diag'].append(results_)
        results['R_vis_duration'].append(R_vis_duration)

        # maintenance of early classifiers
        results_ = list()
        for toi in [[.100, .150], [.170, .220]]:
            y_error = get_predict_error(gat, toi=toi, typ='gat')
            results_.append(angle_acc(y_error, axis=0))
        results['early_maintain'].append(results_)

    # Save
    results['times'] = times
    results['bins'] = bins
    fname = paths('score', subject='fsaverage', analysis=analysis + '-tuning')
    with open(fname, 'wb') as f:
        pickle.dump(results, f)