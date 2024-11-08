import React, { useState, useEffect } from 'react';
import '../Admin.css';
import Config from "../config";
let ApiUrl = Config.API_URL;

function Admin() {
    const [selectedFile, setSelectedFile] = useState(null);
    const [error, setError] = useState('');
    const [fileList, setFileList] = useState([]); // Состояние для списка файлов


    // Обработчик изменения файла
    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file && file.type !== 'application/pdf') {
            setError('Файл должен быть в формате .pdf');
            setSelectedFile(null);
        } else {
            setError('');
            setSelectedFile(file);
        }
    };

    // Обработчик отправки формы
    const handleSubmit = async (event) => {
        event.preventDefault();
        if (!selectedFile) {
            alert('Выберите файл для загрузки');
            return;
        }

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const response = await fetch(`${ApiUrl}/admin/create_file/${selectedFile.name}`, {
                method: 'POST',
                body: formData,
            });
            if (response.ok) {
                alert('Файл успешно загружен!');
                setFileList([...fileList, selectedFile.name]); // Добавляем файл в список
                setSelectedFile(null); // Сброс выбранного файла
            } else {
                alert('Ошибка при загрузке файла');
            }
        } catch (error) {
            console.error('Ошибка:', error);
            alert('Ошибка при отправке файла');
        }
    };

    // Обработчик удаления файла
    const handleDelete = async (filename) => {
        try {
            const response = await fetch(`${ApiUrl}/admin/delete_file/${filename}`, {
                method: 'DELETE',
            });
            if (response.ok) {
                setFileList(fileList.filter(file => file !== filename)); // Удаление из списка
            } else {
                alert('Ошибка при удалении файла');
            }
        } catch (error) {
            console.error('Ошибка:', error);
            alert('Ошибка при удалении файла');
        }
    };

    return (
        <div className="page-container">
            <h2>Администраторская Панель</h2>
            <div className="admin-panel">
                {/* Выбор файла */}
                <div className="mb-3">
                    <label htmlFor="formFile" className="form-label">Выберите файл для загрузки</label>
                    <input
                        className="form-control"
                        type="file"
                        id="formFile"
                        onChange={handleFileChange}
                    />
                </div>

                {/* Сообщение об ошибке */}
                {error && <p className="error-message">{error}</p>}

                {/* Кнопка отправки */}
                <button className="submit-button" onClick={handleSubmit}>
                    Задать новый файл
                </button>

                {/* Список загруженных файлов */}
                <div className="file-list">
                    {fileList.length > 0 && <h3>Загруженные файлы:</h3>}                    <ul>
                        {fileList.map((file, index) => (
                            <li key={index} className="file-item">
                                {file}
                                <button
                                    className="delete-button"
                                    onClick={() => handleDelete(file)}
                                >
                                    &times;
                                </button>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </div>
    );
}

export default Admin;
