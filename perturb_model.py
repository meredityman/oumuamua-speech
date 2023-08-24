import torch
import argparse
import random

def perturb_weights(state_dict, perturbation_scale, perturbation_prob):
    for key, value in state_dict.items():
        print(key)
        if isinstance(value, torch.Tensor):
            # try:
            #     layer = int(key.split(".")[1])

            #     if(layer < 2 or layer > 7):
            #         continue
            # except:
            #     continue
            if(key.startswith("encoder")):
            # if(key == "encoder.prenet.proj.weight"):
                if random.random() < perturbation_prob:
                    noise = torch.randn(value.size(), device=value.device) * perturbation_scale
                    state_dict[key] += noise
    return state_dict


def main(args):
    # Load the checkpoint file (.pth) as a state_dict
    state_dict = torch.load(args.input_path)

    # Perturb the weights directly for an unknown model
    state_dict['model'] = perturb_weights(state_dict['model'], args.perturbation_scale, args.perturbation_prob)

    # Save the perturbed model checkpoint
    torch.save(state_dict, args.output_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load a PyTorch model, perturb its weights, and save the perturbed model.')
    parser.add_argument('--input_path', type=str, required=True, help='Path to the input model checkpoint file (.pth).')
    parser.add_argument('--output_path', type=str, required=True, help='Path to save the perturbed model checkpoint.')
    parser.add_argument('--perturbation_scale', type=float, default=0.1, help='Magnitude of random perturbation for weights.')
    parser.add_argument('--perturbation_prob', type=float, default=0.05, help='Probability of perturbing each weight.')

    args = parser.parse_args()
    main(args)
