import os
import torch

from connectomics.utils.system import get_args, init_devices
from connectomics.config import load_cfg, save_all_cfg
from ganloss_ssl.trainer import TrainerGANLoss
from ganloss_ssl.config import add_ganloss_config


def main():
    args = get_args()
    cfg = load_cfg(args, freeze=False, add_cfg_func=add_ganloss_config)
    device = init_devices(args, cfg)
    
    if args.local_rank == 0 or args.local_rank is None:
        # In distributed training, only print and save the configurations 
        # using the node with local_rank=0.
        print("PyTorch: ", torch.__version__)
        print(cfg)

        if not os.path.exists(cfg.DATASET.OUTPUT_PATH):
            print('Output directory: ', cfg.DATASET.OUTPUT_PATH)
            os.makedirs(cfg.DATASET.OUTPUT_PATH)
            save_all_cfg(cfg, cfg.DATASET.OUTPUT_PATH)

    # start training or inference
    mode = 'test' if args.inference else 'train'
    trainer = TrainerGANLoss(
        cfg, device=device, mode=mode,
        rank=args.local_rank, checkpoint=args.checkpoint)

    # Start training or inference:
    assert cfg.DATASET.DO_CHUNK_TITLE == 0 # TileDataset case is not supported
    test_func = trainer.test_singly if cfg.INFERENCE.DO_SINGLY else trainer.test
    test_func() if args.inference else trainer.train()

    print("Rank: {}. Device: {}. Process is finished!".format(
          args.local_rank, device))


if __name__ == "__main__":
    main()
