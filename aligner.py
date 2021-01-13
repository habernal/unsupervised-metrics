from transformers import BertModel, BertTokenizer, BertConfig
from word_mover_utils import word_mover_align
from torch.cuda import is_available as cuda_is_available
from random import sample
import logging

class XMoverAligner:

    def __init__(
        self,
        model_name='bert-base-multilingual-cased',
        do_lower_case=False,
        device="cuda" if cuda_is_available() else "cpu",
        k = 5,
        n_gram = 1,
        word_mover_batch_size = 64,
        nearest_neighbor_batch_size = 1000000
    ):
        logging.info("Using device \"%s\" for computations.", device)
        config = BertConfig.from_pretrained(model_name, output_hidden_states=True, output_attentions=True)

        self.tokenizer = BertTokenizer.from_pretrained(model_name, do_lower_case=do_lower_case)
        self.model = BertModel.from_pretrained(model_name, config=config)
        self.model.to(device)
        self.device = device
        self.n_gram = n_gram
        self.word_mover_batch_size = word_mover_batch_size

    def align_data(self, source_data, target_data):
        return word_mover_align(self.model, self.tokenizer, source_data, target_data,
                self.n_gram, self.word_mover_batch_size, self.device)

    def accuracy_on_data(self, ref_source_data, ref_target_data):
        pairs = self.align_data(ref_source_data, sample(ref_target_data,
            len(ref_target_data)))

        return sum([ref == out for ref, (_, out) in zip(ref_target_data,
            pairs)]) / len(ref_source_data)
        
