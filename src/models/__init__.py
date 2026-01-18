"""Model classes and utilities."""

import pandas as pd
from optbinning import OptimalBinning


class WoETransformerV2:
    """WoE transformer with monotonic binning for credit scorecard."""

    def __init__(self):
        self.binners = {}
        self.woe_maps = {}

    def fit(self, X, y, features):
        """Fit optimal binning for each feature."""
        for feat in features:
            optb = OptimalBinning(
                name=feat,
                dtype="numerical",
                solver="cp",
                monotonic_trend="auto"
            )
            optb.fit(X[feat].values, y.values)
            self.binners[feat] = optb

            # Store WoE mapping
            binning_table = optb.binning_table.build()
            self.woe_maps[feat] = binning_table[['Bin', 'WoE']].set_index('Bin')['WoE'].to_dict()

        return self

    def transform(self, X, features):
        """Transform features to WoE values."""
        X_woe = pd.DataFrame(index=X.index)
        for feat in features:
            X_woe[f'{feat}_woe'] = self.binners[feat].transform(X[feat].values, metric='woe')
        return X_woe

    def get_scorecard_table(self, model, feature_names, factor, offset):
        """Convert to scorecard with proper intercept handling."""
        scorecard = []

        # Base score from intercept
        intercept = model.intercept_[0]
        base_points = round(offset - factor * intercept)

        scorecard.append({
            'Feature': 'BASE_SCORE',
            'Bin': 'N/A',
            'WoE': None,
            'Points': base_points
        })

        # Feature points
        for i, feat in enumerate(feature_names):
            original_feat = feat.replace('_woe', '')
            coef = model.coef_[0][i]

            for bin_label, woe in self.woe_maps[original_feat].items():
                if bin_label not in ['Totals', 'Special']:
                    points = round(-factor * coef * woe)
                    scorecard.append({
                        'Feature': original_feat,
                        'Bin': str(bin_label),
                        'WoE': round(woe, 4) if woe is not None else None,
                        'Points': points
                    })

        return pd.DataFrame(scorecard)
