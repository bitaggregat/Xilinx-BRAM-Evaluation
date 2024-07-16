import argparse
from enum import Enum, auto

parser = argparse.ArgumentParser(
    description="Script that creates BRAM template based on text file (for debugging purposes)."
)
parser.add_argument(
    "-i",
    "--input_file",
    help="Path to text file that will be used used as bram content",
    required=True,
)
parser.add_argument(
    "-t",
    "--output_type",
    help="Type of output. Verilog fragment or coe.",
    choices=["verilog", "coe"],
    default="verilog"
)
parser.add_argument("-o", "--output_file", help="Path to output file.")


class Architecture(Enum):
    xc7_36k = auto()
    xc7_36k_parity = auto()


parser.add_argument(
    "-a",
    "--architecture",
    help="Type of bram that will be used. Currently only XC7 36K",
    choices=[arch.name for arch in Architecture],
    default=Architecture.xc7_36k
)


class VerilogFragment:
    template_func = None
    size = None
    text = None

    def __init__(self, arch: Architecture, text: str):
        self.text = text
        match arch:
            case Architecture.xc7_36k:
                self.template_func = self.xc7_36k_template
                self.size = 0x7F
            case Architecture.xc7_36k_parity:
                self.template_func = self.xc7_36k_parity_templatte
                self.size = 0x0F
            case _:
                raise Exception(f"Error BRAM Architecture {arch} not yet implemented")

    def xc7_36k_template(self, index: int, content: str) -> str:
        idx_str = ("%02x" % index).upper()
        return f"\t.INIT_{idx_str}(256'h{content}),"

    def xc7_36k_parity_templatte(self, index: int, content: str) -> str:
        idx_str = ("%02x" % index).upper()
        return f"\t.INITP_{idx_str}(256'h{content}),"

    def generate_fragment(self) -> str:
        return "\n".join(
            [
                self.template_func(i, self.text[i * 32 : (i + 1) * 32].encode()[::-1].hex())
                for i in range(self.size + 1)
            ]
        )


if __name__ == "__main__":
    args = vars(parser.parse_args())

    output_file = args["output_file"]
    output_type = args["output_type"]
    architecture = Architecture[args["architecture"]]
    input_file = args["input_file"]

    with open(input_file) as f:
        text = f.read()

    content = None
    match output_type:
        case "verilog":
            verilog_fragment = VerilogFragment(architecture, text)
            content = verilog_fragment.generate_fragment()

        case "coe":
            raise Exception("Not implemented")

        case _:
            raise Exception("Error: This is bad because it shouldn't happen")

    if output_file is not None:
        with open(output_file, mode="w") as f:
            f.write(content)
    else:
        print(content)
