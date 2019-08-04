#! /usr/bin/env python3

from pyspark.sql.types import *
import numpy as np
import pandas as pd


def logistic_model_eval_sdf(data_sdf, par, fit_intercept):
    """Evaluate model performance


    par p-column matrix, where each column corresponds to one method

    """

    ## Create schema fields
    schema_fields = []
    for j in par.columns:
        schema_fields.append(StructField(j, DoubleType(), True))
    schema_beta2 = StructType(schema_fields)

    @pandas_udf(schema_beta2, PandasUDFType.GROUPED_MAP)
    def logistic_model_eval_udf(sample_df):
        return logistic_model_eval(sample_df=sample_df,
                                   Y_name=Y_name,
                                   fit_intercept=fit_intercept,
                                   par=par,
                                   dummy_info=dummy_info,
                                   data_info=data_info)

    # Calculate log likelihood for partitioned data
    model_mapped_sdf = data_sdf.groupby("partition_id").apply(logistic_model_eval_udf)

    # groupped_sdf = model_mapped_sdf.groupby('par_id')
    groupped_sdf_sum = model_mapped_sdf.groupby().sum(*model_mapped_sdf.columns[0:])
    groupped_pdf_sum = groupped_sdf_sum.toPandas()

    return(groupped_pdf_sum)
