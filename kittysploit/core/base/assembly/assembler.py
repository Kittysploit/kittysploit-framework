from keystone import *
from kittysploit.core.base.io import print_error

class Assembler:
    
    def __init__(self, current_arch=None):
        
        self.current_arch = current_arch
        
        self.all_archs = { # Keystone - Assembler
				'x16':     (KS_ARCH_X86,     KS_MODE_16),
				'x86':     (KS_ARCH_X86,     KS_MODE_32),
				'x64':     (KS_ARCH_X86,     KS_MODE_64),
				'arm':     (KS_ARCH_ARM,     KS_MODE_ARM),
				'arm_t':   (KS_ARCH_ARM,     KS_MODE_THUMB),
				'arm64':   (KS_ARCH_ARM64,   KS_MODE_LITTLE_ENDIAN),
				'mips32':  (KS_ARCH_MIPS,    KS_MODE_MIPS32),
				'mips64':  (KS_ARCH_MIPS,    KS_MODE_MIPS64)
				}
        
    def assemble(self, code=""):
        if self.current_arch in self.all_archs:
            try:
                ks = Ks(self.all_archs[self.current_arch][0], self.all_archs[self.current_arch][1])
                encoding = ks.asm(code)
                return encoding
            except KsError as e:
                print_error(str(e))
                return