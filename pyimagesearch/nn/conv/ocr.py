from tensorflow.keras.layers import (
    Conv2D, MaxPooling2D, GRU, Bidirectional, TimeDistributed,
    Input, Dense, Activation, Reshape, BatchNormalization
)


class OCR:
    @staticmethod
    def build(input_size, pool_size, output_size):
        conv_filters = 16
        kernel_size = (3, 3)
        time_dense_size = 32
        rnn_size = 512

        input_data = Input(name="input", shape=input_size)

        cnn = Conv2D(conv_filters, kernel_size, padding='same', kernel_initializer='he_normal')(input_data)
        cnn = BatchNormalization()(cnn)
        cnn = Activation('relu')(cnn)
        cnn = MaxPooling2D(pool_size=(pool_size, pool_size))(cnn)

        cnn = Conv2D(conv_filters, kernel_size, padding='same', kernel_initializer='he_normal')(cnn)
        cnn = BatchNormalization()(cnn)
        cnn = Activation('relu')(cnn)
        cnn = MaxPooling2D(pool_size=(pool_size, pool_size))(cnn)

        # CNN to RNN
        shape = cnn.get_shape()
        bgru = Reshape((shape[1], shape[2] * shape[3]))(cnn)

        bgru = Bidirectional(GRU(units=rnn_size, return_sequences=True, dropout=0.5))(bgru)
        bgru = TimeDistributed(Dense(units=time_dense_size))(bgru)

        bgru = Bidirectional(GRU(units=rnn_size, return_sequences=True, dropout=0.5))(bgru)
        output_data = TimeDistributed(Dense(units=output_size, activation="softmax"))(bgru)

        return input_data, output_data
