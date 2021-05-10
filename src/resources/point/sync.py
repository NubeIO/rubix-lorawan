from rubix_http.resource import RubixResource

from src.models.model_point_store import PointStoreModel


class LPToGPSync(RubixResource):

    @classmethod
    def get(cls):
        PointStoreModel.sync_points_values_lp_to_gbp_process(gp=True, bp=False)


class LPToBPSync(RubixResource):

    @classmethod
    def get(cls):
        PointStoreModel.sync_points_values_lp_to_gbp_process(gp=False, bp=True)
