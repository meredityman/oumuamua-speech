import torch
import argparse
import random
from pathlib import Path
import shutil

def perturb_weights(state_dict, perturbation_scale, perturbation_prob):
    for key, value in state_dict.items():
        if isinstance(value, torch.Tensor):
            # try:
            #     layer = int(key.split(".")[1])

            #     if(layer < 2 or layer > 7):
            #         continue
            # except:
            #     continue
            if(key.startswith("text_encoder.encoder.attn_layers.") or key.startswith("duration_predictor.flows.2.")) :
                print(key)
            # if(key == "encoder.prenet.proj.weight"):
                if random.random() < perturbation_prob:
                    noise = torch.randn(value.size(), device=value.device) * perturbation_scale
                    state_dict[key] += noise
    return state_dict


def main(args):
    input_path  = Path(args.input_path)
    orig_model  = Path(input_path, "model_file.pth")
    orig_config = Path(input_path, "config.json")

    # Load the checkpoint file (.pth) as a state_dict
    state_dict = torch.load(orig_model)

    # for key, value in state_dict['model'].items():
    #     print(key)

    N = 5
    for i in range(N):
        output_path = Path(args.output_path, f"{input_path.stem}_glitch_{i:04d}")
        output_path.mkdir(exist_ok=True)

        print(f"{i+1}/{N} -> {output_path}")

        perturb_dict = state_dict.copy()

        scale = args.perturbation_scale * ((i+1)/N)
        prob  = args.perturbation_prob  * ((i+1)/N)
        print(f"scale : {scale} | prob : {prob}")
        # Perturb the weights directly for an unknown model
        perturb_dict['model'] = perturb_weights(perturb_dict['model'], scale, prob)

        # Save the perturbed model checkpoint
        torch.save(perturb_dict, Path(output_path, "model_file.pth"))
        shutil.copy(orig_config, Path(output_path, "config.json"))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load a PyTorch model, perturb its weights, and save the perturbed model.')
    parser.add_argument('--input_path', default=".local/share/tts/tts_models--en--ljspeech--vits",
        type=str, help='Path to the input model checkpoint file (.pth).')
    parser.add_argument('--output_path', default=".local/share/tts", 
        type=str, help='Path to save the perturbed model checkpoint.')
    
    parser.add_argument('--perturbation_scale', type=float, default=0.15, help='Magnitude of random perturbation for weights.')
    parser.add_argument('--perturbation_prob', type=float, default=0.15, help='Probability of perturbing each weight.')

    args = parser.parse_args()
    main(args)
