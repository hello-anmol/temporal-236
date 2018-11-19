from util.data_loader import AnimatedDataset
from util.paths import sequences_dir
from os.path import join

if __name__ == "__main__":
    ds = AnimatedDataset(join(sequences_dir, "animated"))
    print(len(ds))
    print(ds[247][0][0].shape)