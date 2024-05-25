from capstone import *
from binascii import unhexlify
from kittysploit.core.base.io import print_error

class Disassembler:
    
    def __init__(self, current_arch=None):
        
        self.current_arch = current_arch
        
        self.all_archs = { # Capstone - Disassembler
					'x16':     (CS_ARCH_X86,     CS_MODE_16),
					'x86':     (CS_ARCH_X86,     CS_MODE_32),
					'x64':     (CS_ARCH_X86,     CS_MODE_64),
					'arm':     (CS_ARCH_ARM,     CS_MODE_ARM),
					'arm_t':   (CS_ARCH_ARM,     CS_MODE_THUMB),
					'arm64':   (CS_ARCH_ARM64,   CS_MODE_LITTLE_ENDIAN),
					'mips32':  (CS_ARCH_MIPS,    CS_MODE_MIPS32),
					'mips64':  (CS_ARCH_MIPS,    CS_MODE_MIPS64),
				}

    def disassemble(self, code=""):
        if self.current_arch in self.all_archs:
            try:
                assembly = []
                md = Cs(self.all_archs[self.current_arch][0], self.all_archs[self.current_arch][1])
                for i in md.disasm(unhexlify(self.cleanup(code)), 0x1000):
                    assembly.append([i.address, i.mnemonic, i.op_str])
                return assembly
            except CsError as e:
                print_error(str(e))
                return

    def cleanup(self, input_str):
        input_str = input_str.replace(" ", "")
        input_str = input_str.replace("\\x", "")
        return input_str.replace("0x", "")