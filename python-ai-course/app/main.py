from __future__ import annotations

import argparse

from app import analytics, storage


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器，提供注册、实时签到、统计和 API 服务入口。"""
    parser = argparse.ArgumentParser(description="ASCII 风格人脸识别签到系统")
    subparsers = parser.add_subparsers(dest="command", required=True)

    register = subparsers.add_parser("register", help="注册用户人脸")
    register.add_argument("--user-id", required=True)
    register.add_argument("--name", required=True)
    register.add_argument("--image", required=True)

    subparsers.add_parser("run", help="启动签到流程")
    subparsers.add_parser("stats", help="查看签到统计")

    serve = subparsers.add_parser("serve", help="启动前端交互 API 服务")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8765)

    demo = subparsers.add_parser("demo-checkin", help="写入一条演示签到记录")
    demo.add_argument("--user-id", default="2026001")
    demo.add_argument("--name", default="测试学生")
    return parser


def handle_register(args) -> None:
    """命令行注册入口：读取图片并训练/更新人脸识别模型。"""
    from app import face_recognize

    face_recognize.register_face(args.user_id, args.name, args.image)
    print(f"注册成功: {args.name} ({args.user_id})")


def handle_stats() -> None:
    """命令行统计入口：输出签到和识别事件的汇总结果。"""
    summary = analytics.summarize_attendance()
    print("签到统计")
    print(summary)


def handle_demo_checkin(args) -> None:
    """写入一条演示签到和对应识别事件，用于无摄像头时展示记录功能。"""
    from app import attendance, events

    event_id = events.next_event_id()
    record = attendance.mark_attendance(args.user_id, args.name, event_id=event_id)
    event_row = events.append_event(
        record["status"],
        user_id=args.user_id,
        name=args.name,
        message="演示签到成功" if record["status"] == "success" else "演示重复签到",
        event_id=event_id,
    )
    print("演示签到结果")
    print(record)
    print("识别事件")
    print(event_row)


def handle_serve(args) -> None:
    """启动后端 API 服务，供 React 前端页面调用。"""
    from app import api_server

    api_server.run_server(args.host, args.port)


def handle_run() -> None:
    """启动命令行实时签到循环：采集画面、检测人脸、识别身份并写入签到。"""
    import cv2

    from app import ascii_render, attendance, camera, config, events, face_detect, face_recognize, preprocess

    known_faces = face_recognize.load_known_faces()
    capture = camera.open_camera()
    print("按 Ctrl+C 退出签到流程。")

    try:
        while True:
            success, frame = capture.read()
            if not success:
                print("读取摄像头帧失败")
                break

            gray_frame = preprocess.prepare_frame(frame, config.FRAME_SCALE)
            locations = face_detect.locate_faces(gray_frame)
            matches = face_recognize.match_faces(
                gray_frame,
                locations,
                known_faces,
                config.LBPH_CONFIDENCE_THRESHOLD,
            )

            status_text = "No face"
            for match in matches:
                if match["matched"]:
                    confidence = f"{match.get('confidence', '')}"
                    event_id = events.next_event_id()
                    record = attendance.mark_attendance(
                        match["user_id"],
                        match["name"],
                        confidence=confidence,
                        event_id=event_id,
                    )
                    events.append_event(
                        record["status"],
                        user_id=match["user_id"],
                        name=match["name"],
                        confidence=confidence,
                        face_count=len(locations),
                        message="签到成功" if record["status"] == "success" else "当天已签到，已拦截重复写入",
                        event_id=event_id,
                    )
                    status_text = f'{match["name"]}: {record["status"]}'
                elif known_faces.recognizer is None:
                    events.append_event(
                        "no_model",
                        face_count=len(locations),
                        message="检测到人脸，但尚未训练识别模型",
                    )
                    status_text = "No trained model"
                else:
                    events.append_event(
                        "unknown",
                        confidence=f"{match.get('confidence', '')}",
                        face_count=len(locations),
                        message="检测到人脸，但未匹配到注册用户",
                    )
                    status_text = "Unknown user"

            ascii_output = ascii_render.frame_to_ascii(frame, config.ASCII_WIDTH, config.ASCII_CHARS)
            print("\033[2J\033[H", end="")
            print(ascii_output)
            print()
            print(f"Status: {status_text}")

            cv2.waitKey(1)
    except KeyboardInterrupt:
        print("\n签到流程已退出。")
    finally:
        capture.release()


def main() -> None:
    """程序主入口：初始化数据目录，解析命令并分发到对应处理函数。"""
    storage.ensure_data_dirs()
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "register":
        handle_register(args)
    elif args.command == "run":
        handle_run()
    elif args.command == "stats":
        handle_stats()
    elif args.command == "serve":
        handle_serve(args)
    elif args.command == "demo-checkin":
        handle_demo_checkin(args)


if __name__ == "__main__":
    main()
