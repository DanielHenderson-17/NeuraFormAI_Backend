from OpenGL.GL import *

class ShaderManager:
    def __init__(self, vertex_shader_path: str, fragment_shader_path: str):
        self.program = glCreateProgram()
        self.vertex_shader = self._compile_shader(vertex_shader_path, GL_VERTEX_SHADER)
        self.fragment_shader = self._compile_shader(fragment_shader_path, GL_FRAGMENT_SHADER)

        glAttachShader(self.program, self.vertex_shader)
        glAttachShader(self.program, self.fragment_shader)
        glLinkProgram(self.program)

        if glGetProgramiv(self.program, GL_LINK_STATUS) != GL_TRUE:
            info = glGetProgramInfoLog(self.program)
            raise RuntimeError(f"Shader link failed: {info}")

    def _compile_shader(self, filepath, shader_type):
        with open(filepath, "r", encoding="utf-8") as file:
            source = file.read()

        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)

        if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
            info = glGetShaderInfoLog(shader)
            raise RuntimeError(f"Shader compile failed ({filepath}): {info}")
        return shader

    def use(self):
        glUseProgram(self.program)

    def stop(self):
        glUseProgram(0)

    def get_uniform_location(self, name: str):
        return glGetUniformLocation(self.program, name)

    def __del__(self):
        if hasattr(self, "program"):
            glDeleteProgram(self.program)
