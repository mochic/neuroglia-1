.. _api_ref:

.. currentmodule:: neuroglia

API reference
=============

.. _spike_api:

Spike transformers
------------------

.. autosummary::
   :toctree: generated/

    spike.Binner
    spike.Smoother
    nwb.SpikeTablizer

.. _trace_api:

Trace transformers
------------------

.. autosummary::
   :toctree: generated/

    trace.Binarizer
    trace.EdgeDetector
    trace.WhenTrueFinder
    calcium.CalciumInferer
    calcium.MedianFilterDetrender
    calcium.SavGolFilterDetrender
    calcium.EventRescaler


.. _event_api:

Event transformers
------------------

.. autosummary::
   :toctree: generated/

    event.PeriEventSpikeSampler
    event.PeriEventTraceSampler

.. _tensor_api:

Tensor transformers
-------------------

.. autosummary::
   :toctree: generated/

    tensor.ResponseReducer

Datasets
-------------------

.. autosummary::
   :toctree: generated/

    datasets.fetch_rat_hippocampus_foraging
